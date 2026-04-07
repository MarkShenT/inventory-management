import { ref, computed } from 'vue'

// Shared sidebar state (singleton pattern)
const savedState = localStorage.getItem('sidebar-collapsed')
const isCollapsed = ref(savedState === 'true')

const COLLAPSE_BREAKPOINT = 1024

export function useSidebar() {
  const sidebarWidth = computed(() => isCollapsed.value ? 64 : 240)

  const toggleCollapse = () => {
    isCollapsed.value = !isCollapsed.value
    localStorage.setItem('sidebar-collapsed', String(isCollapsed.value))
  }

  const collapse = () => {
    isCollapsed.value = true
    localStorage.setItem('sidebar-collapsed', 'true')
  }

  // Auto-collapse on small screens via matchMedia listener.
  // Returns a cleanup function for onUnmounted.
  const setupMediaQuery = () => {
    const mq = window.matchMedia(`(max-width: ${COLLAPSE_BREAKPOINT}px)`)
    const handler = (e) => {
      if (e.matches) collapse()
    }
    mq.addEventListener('change', handler)
    if (mq.matches) collapse()
    return () => mq.removeEventListener('change', handler)
  }

  return {
    isCollapsed,
    sidebarWidth,
    toggleCollapse,
    setupMediaQuery
  }
}
