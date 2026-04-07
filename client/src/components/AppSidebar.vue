<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <!-- Header: Logo -->
    <div class="sidebar-header">
      <div class="logo-icon">CC</div>
      <div v-show="!isCollapsed" class="logo-text">
        <h1>{{ t('nav.companyName') }}</h1>
        <span>{{ t('nav.subtitle') }}</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: $route.path === item.path }"
        :title="item.label || t(item.labelKey)"
      >
        <span class="nav-icon">
          <!-- Overview -->
          <svg v-if="item.icon === 'overview'" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="2" width="7" height="7" rx="1"/>
            <rect x="11" y="2" width="7" height="7" rx="1"/>
            <rect x="2" y="11" width="7" height="7" rx="1"/>
            <rect x="11" y="11" width="7" height="7" rx="1"/>
          </svg>
          <!-- Inventory -->
          <svg v-else-if="item.icon === 'inventory'" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 7l7-4 7 4v6l-7 4-7-4V7z"/>
            <path d="M3 7l7 4 7-4"/>
            <path d="M10 11v7"/>
          </svg>
          <!-- Orders -->
          <svg v-else-if="item.icon === 'orders'" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M7 3H5a1 1 0 00-1 1v12a1 1 0 001 1h10a1 1 0 001-1V4a1 1 0 00-1-1h-2"/>
            <rect x="7" y="1" width="6" height="3" rx="1"/>
            <path d="M8 9h4M8 12h2"/>
          </svg>
          <!-- Finance -->
          <svg v-else-if="item.icon === 'finance'" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="10" cy="10" r="8"/>
            <path d="M10 5v10M7.5 7.5c0-1 1-1.5 2.5-1.5s2.5.5 2.5 1.5-1 1.5-2.5 2-2.5 1-2.5 2 1 1.5 2.5 1.5 2.5-.5 2.5-1.5"/>
          </svg>
          <!-- Demand -->
          <svg v-else-if="item.icon === 'demand'" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 17l4-4 3 3 7-7"/>
            <path d="M14 9h3v3"/>
          </svg>
          <!-- Reports -->
          <svg v-else-if="item.icon === 'reports'" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="10" width="3" height="7" rx="0.5"/>
            <rect x="8.5" y="6" width="3" height="11" rx="0.5"/>
            <rect x="14" y="3" width="3" height="14" rx="0.5"/>
          </svg>
          <!-- Restocking -->
          <svg v-else-if="item.icon === 'restocking'" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 10a7 7 0 0113.6-2.3M17 10a7 7 0 01-13.6 2.3"/>
            <path d="M16.7 3v4.7H12M3.3 17v-4.7H8"/>
          </svg>
        </span>
        <span v-show="!isCollapsed" class="nav-label">{{ item.label || t(item.labelKey) }}</span>
      </router-link>
    </nav>

    <!-- Footer: toggle + lang + profile -->
    <div class="sidebar-footer">
      <button @click="toggleCollapse" class="collapse-toggle" :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'">
        <svg
          class="chevron-icon"
          :class="{ 'chevron-rotated': isCollapsed }"
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 4l-6 6 6 6"/>
        </svg>
      </button>
      <LanguageSwitcher :compact="isCollapsed" />
      <ProfileMenu
        :compact="isCollapsed"
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </aside>
</template>

<script>
import { onMounted, onUnmounted } from 'vue'
import { useSidebar } from '../composables/useSidebar'
import { useI18n } from '../composables/useI18n'
import { useAuth } from '../composables/useAuth'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

export default {
  name: 'AppSidebar',
  components: {
    LanguageSwitcher,
    ProfileMenu
  },
  emits: ['show-profile-details', 'show-tasks'],
  setup() {
    const { isCollapsed, sidebarWidth, toggleCollapse, setupMediaQuery } = useSidebar()
    const { t } = useI18n()
    const { currentUser } = useAuth()

    const navItems = [
      { path: '/',           labelKey: 'nav.overview',       icon: 'overview'   },
      { path: '/inventory',  labelKey: 'nav.inventory',      icon: 'inventory'  },
      { path: '/orders',     labelKey: 'nav.orders',         icon: 'orders'     },
      { path: '/spending',   labelKey: 'nav.finance',        icon: 'finance'    },
      { path: '/demand',     labelKey: 'nav.demandForecast', icon: 'demand'     },
      { path: '/reports',    labelKey: 'nav.reports', label: 'Reports', icon: 'reports' },
      { path: '/restocking', labelKey: 'nav.restocking',     icon: 'restocking' }
    ]

    let cleanupMediaQuery = null

    onMounted(() => {
      cleanupMediaQuery = setupMediaQuery()
    })

    onUnmounted(() => {
      if (cleanupMediaQuery) cleanupMediaQuery()
    })

    return {
      isCollapsed,
      sidebarWidth,
      toggleCollapse,
      t,
      currentUser,
      navItems
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  position: sticky;
  top: 0;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
  z-index: 100;
}

.sidebar.collapsed {
  width: 64px;
  min-width: 64px;
}

/* Header */
.sidebar-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: #0f172a;
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.logo-text {
  overflow: hidden;
}

.logo-text h1 {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  line-height: 1.25;
}

.logo-text span {
  font-size: 0.75rem;
  color: #64748b;
  white-space: nowrap;
  line-height: 1.3;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 0.5rem 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1rem;
  color: #64748b;
  font-weight: 500;
  font-size: 0.875rem;
  border-radius: 6px;
  margin: 0.125rem 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-decoration: none;
  transition: all 0.15s ease;
}

.nav-item:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.nav-item.active {
  color: #2563eb;
  background: #eff6ff;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Footer */
.sidebar-footer {
  margin-top: auto;
  padding: 0.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex-shrink: 0;
}

.collapse-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #64748b;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.collapse-toggle:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.chevron-icon {
  transition: transform 0.25s ease;
  flex-shrink: 0;
}

.chevron-rotated {
  transform: rotate(180deg);
}
</style>
