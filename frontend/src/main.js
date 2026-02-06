import './style.css'
import { appState } from './state.js'
import { fetchLeaderboard, fetchHealth } from './api/leaderboard.js'
import { KingdomSelector } from './components/KingdomSelector.js'
import { MetricSelector } from './components/MetricSelector.js'
import { DateSelector } from './components/DateSelector.js'
import { LimitInput } from './components/LimitInput.js'
import { LeaderboardTable } from './components/LeaderboardTable.js'

// Initialize components
const kingdomSelector = new KingdomSelector('kingdom-selector')
const metricSelector = new MetricSelector('metric-selector')
const dateSelector = new DateSelector('date-selector')
const limitInput = new LimitInput('limit-input')
const leaderboardTable = new LeaderboardTable('leaderboard-container')

// DOM elements
const loadBtn = document.getElementById('load-btn')
const statusDiv = document.getElementById('status')

// Load leaderboard on button click
loadBtn.addEventListener('click', async () => {
  const state = appState.get()
  const { kingdom, metric, dt, limit } = state
  
  // Basic validation
  if (!kingdom) {
    showStatus('Please enter a kingdom ID', 'error')
    return
  }
  
  if (!state.useLatest && !dt) {
    showStatus('Please enter a date or select "Use Latest"', 'error')
    return
  }
  
  // Show loading state
  showStatus('Loading leaderboard...', 'loading')
  appState.set({ loading: true, error: null })
  
  try {
    const data = await fetchLeaderboard({ kingdom, metric, dt, limit })
    
    // Update state with data
    appState.set({ 
      leaderboardData: data, 
      loading: false 
    })
    
    showStatus(`Loaded ${data.rows.length} players for kingdom ${data.kingdom} (${data.dt})`, 'success')
  } catch (error) {
    appState.set({ 
      error: error.message, 
      loading: false 
    })
    showStatus(`Error: ${error.message}`, 'error')
    console.error('Failed to load leaderboard:', error)
  }
})

// Helper to show status messages
function showStatus(message, type = 'info') {
  statusDiv.textContent = message
  statusDiv.className = `status ${type}`
}

// Check API health on page load
async function checkHealth() {
  try {
    const health = await fetchHealth()
    console.log('API health check:', health)
    showStatus(`API is healthy (${health.service} v${health.version})`, 'success')
    appState.set({ apiHealthy: true })
  } catch (error) {
    showStatus(`Warning: API health check failed - ${error.message}`, 'warning')
    console.warn('API health check failed:', error)
    appState.set({ apiHealthy: false })
  }
}

// Initialize app
console.log('RoK Leaderboard Frontend initialized')
console.log('API URL:', import.meta.env.VITE_API_URL)
checkHealth()
