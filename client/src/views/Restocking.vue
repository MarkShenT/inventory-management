<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="placedOrder" class="card success-card">
      <div class="success-header">
        <div class="success-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <h3>{{ t('restocking.orderSuccess') }}</h3>
      </div>
      <div class="success-details">
        <div class="success-detail">
          <span class="detail-label">{{ t('restocking.orderNumber') }}</span>
          <span class="detail-value order-number">{{ placedOrder.order_number }}</span>
        </div>
        <div class="success-detail">
          <span class="detail-label">{{ t('restocking.expectedDelivery') }}</span>
          <span class="detail-value">{{ formatDate(placedOrder.expected_delivery) }}</span>
        </div>
        <div class="success-detail">
          <span class="detail-label">{{ t('submittedOrders.leadTime') }}</span>
          <span class="detail-value">{{ t('submittedOrders.days', { count: 14 }) }}</span>
        </div>
      </div>
      <button class="btn-primary" @click="resetOrder">{{ t('restocking.placeAnother') }}</button>
    </div>

    <template v-else>
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
        </div>
        <div class="budget-content">
          <div class="budget-display">{{ formatCurrency(budget) }}</div>
          <input
            type="range"
            class="budget-slider"
            v-model.number="budget"
            :min="10000"
            :max="500000"
            :step="5000"
          />
          <div class="slider-labels">
            <span>{{ formatCurrency(10000) }}</span>
            <span>{{ formatCurrency(500000) }}</span>
          </div>
        </div>
        <div v-if="recommendations" class="budget-stats">
          <div class="budget-stat">
            <span class="budget-stat-label">{{ t('restocking.totalCost') }}</span>
            <span class="budget-stat-value">{{ formatCurrency(recommendations.total_cost) }}</span>
          </div>
          <div class="budget-stat">
            <span class="budget-stat-label">{{ t('restocking.remaining') }}</span>
            <span class="budget-stat-value" :class="{ 'over-budget': recommendations.total_cost > budget }">
              {{ formatCurrency(budget - recommendations.total_cost) }}
            </span>
          </div>
          <div class="budget-stat">
            <span class="budget-stat-label">{{ t('restocking.itemsSelected') }}</span>
            <span class="budget-stat-value">{{ recommendations.items.length }}</span>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="recommendations">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('restocking.itemsSelected') }}</h3>
          </div>
          <div v-if="recommendations.items.length === 0" class="empty-state">
            {{ t('restocking.noRecommendations') }}
          </div>
          <div v-else class="table-container">
            <table>
              <thead>
                <tr>
                  <th>{{ t('restocking.table.sku') }}</th>
                  <th>{{ t('restocking.table.itemName') }}</th>
                  <th>{{ t('restocking.table.forecastedDemand') }}</th>
                  <th>{{ t('restocking.table.currentStock') }}</th>
                  <th>{{ t('restocking.table.restockQty') }}</th>
                  <th>{{ t('restocking.table.unitCost') }}</th>
                  <th>{{ t('restocking.table.totalCost') }}</th>
                  <th>{{ t('restocking.table.priority') }}</th>
                  <th>{{ t('restocking.table.reason') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in recommendations.items" :key="item.sku">
                  <td><strong>{{ item.sku }}</strong></td>
                  <td>{{ item.name }}</td>
                  <td>{{ item.forecasted_demand.toLocaleString() }}</td>
                  <td>{{ item.current_stock.toLocaleString() }}</td>
                  <td><strong>{{ item.restock_quantity.toLocaleString() }}</strong></td>
                  <td>{{ formatCurrency(item.unit_cost) }}</td>
                  <td>{{ formatCurrency(item.total_cost) }}</td>
                  <td>
                    <span :class="['badge', item.priority]">{{ t(`priority.${item.priority}`) }}</span>
                  </td>
                  <td class="reason-cell">{{ item.reason }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="summary-bar">
          <div class="summary-stats">
            <div class="summary-stat">
              <span class="summary-label">{{ t('restocking.itemsSelected') }}</span>
              <span class="summary-value">{{ recommendations.items.length }}</span>
            </div>
            <div class="summary-stat">
              <span class="summary-label">{{ t('restocking.totalCost') }}</span>
              <span class="summary-value">{{ formatCurrency(recommendations.total_cost) }}</span>
            </div>
            <div class="summary-stat">
              <span class="summary-label">{{ t('restocking.remaining') }}</span>
              <span class="summary-value" :class="{ 'over-budget': recommendations.total_cost > budget }">
                {{ formatCurrency(budget - recommendations.total_cost) }}
              </span>
            </div>
          </div>
          <button
            class="btn-primary"
            :disabled="recommendations.items.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()
    const loading = ref(false)
    const error = ref(null)
    const budget = ref(100000)
    const recommendations = ref(null)
    const submitting = ref(false)
    const placedOrder = ref(null)

    const loadRecommendations = async () => {
      loading.value = true
      error.value = null
      try {
        recommendations.value = await api.getRestockingRecommendations(budget.value)
      } catch (err) {
        error.value = 'Failed to load restocking recommendations: ' + err.message
      } finally {
        loading.value = false
      }
    }

    let debounceTimer = null
    watch(budget, () => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(loadRecommendations, 300)
    })

    const placeOrder = async () => {
      if (!recommendations.value || recommendations.value.items.length === 0) return

      submitting.value = true
      error.value = null
      try {
        const orderData = {
          items: recommendations.value.items.map(item => ({
            sku: item.sku,
            name: item.name,
            quantity: item.restock_quantity,
            unit_cost: item.unit_cost
          })),
          budget_used: recommendations.value.total_cost
        }
        placedOrder.value = await api.placeRestockingOrder(orderData)
      } catch (err) {
        error.value = 'Failed to place restocking order: ' + err.message
      } finally {
        submitting.value = false
      }
    }

    const resetOrder = () => {
      placedOrder.value = null
      loadRecommendations()
    }

    const formatCurrency = (value) => {
      if (value == null) return '-'
      const symbol = currentCurrency.value === 'JPY' ? '¥' : '$'
      return symbol + Math.round(value).toLocaleString()
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      if (isNaN(date.getTime())) return dateStr
      return date.toLocaleDateString()
    }

    onMounted(loadRecommendations)

    return {
      t,
      loading,
      error,
      budget,
      recommendations,
      submitting,
      placedOrder,
      placeOrder,
      resetOrder,
      formatCurrency,
      formatDate
    }
  }
}
</script>

<style scoped>
.budget-card {
  margin-bottom: 1.25rem;
}

.budget-content {
  padding: 1rem 0;
}

.budget-display {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 1rem;
  text-align: center;
}

.budget-slider {
  width: 100%;
  height: 6px;
  appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(37, 99, 235, 0.4);
  transition: background 0.15s ease;
}

.budget-slider::-webkit-slider-thumb:hover {
  background: #1d4ed8;
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: none;
  box-shadow: 0 1px 4px rgba(37, 99, 235, 0.4);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.budget-stats {
  display: flex;
  gap: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
  margin-top: 1rem;
}

.budget-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.budget-stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.budget-stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.budget-stat-value.over-budget {
  color: #dc2626;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.reason-cell {
  color: #64748b;
  font-style: italic;
}

.summary-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.summary-stats {
  display: flex;
  gap: 2.5rem;
}

.summary-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.summary-value.over-budget {
  color: #dc2626;
}

.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.success-card {
  border-left: 4px solid #10b981;
  margin-bottom: 1.25rem;
}

.success-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.success-icon {
  width: 44px;
  height: 44px;
  background: #d1fae5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #059669;
}

.success-icon svg {
  width: 22px;
  height: 22px;
}

.success-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #059669;
}

.success-details {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f0fdf4;
  border-radius: 8px;
}

.success-detail {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
}

.order-number {
  font-family: 'Courier New', monospace;
  font-size: 1.125rem;
  color: #059669;
}
</style>
