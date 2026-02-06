/**
 * Simple state management for the leaderboard app
 * Uses a reactive pattern with event-based updates
 */

class AppState {
  constructor() {
    this.state = {
      // Query parameters
      kingdom: '3951',
      metric: 'killpoints',
      dt: 'latest',
      useLatest: true,
      limit: 100,
      
      // Data and UI state
      leaderboardData: null,
      loading: false,
      error: null,
      apiHealthy: false,
    }
    
    this.listeners = []
  }
  
  /**
   * Get current state
   */
  get() {
    return { ...this.state }
  }
  
  /**
   * Update state and notify listeners
   */
  set(updates) {
    this.state = { ...this.state, ...updates }
    this.notify()
  }
  
  /**
   * Subscribe to state changes
   */
  subscribe(listener) {
    this.listeners.push(listener)
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }
  
  /**
   * Notify all listeners of state change
   */
  notify() {
    this.listeners.forEach(listener => listener(this.state))
  }
}

// Export singleton instance
export const appState = new AppState()
