/**
 * API client for the RoK leaderboard backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

/**
 * Fetch leaderboard data from the API
 * 
 * @param {Object} params - Query parameters
 * @param {string} params.kingdom - Kingdom ID
 * @param {string} params.metric - Metric name (power, killpoints, kills, deads)
 * @param {string} params.dt - Date (YYYY-MM-DD) or 'latest'
 * @param {number} params.limit - Number of results to return
 * @returns {Promise<Object>} Leaderboard data
 */
export async function fetchLeaderboard({ kingdom, metric, dt = 'latest', limit = 100 }) {
  const params = new URLSearchParams({
    kingdom,
    metric,
    dt,
    limit: limit.toString(),
  })
  
  const url = `${API_BASE_URL}/leaderboard?${params}`
  
  console.log('Fetching leaderboard:', url)
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  
  if (!response.ok) {
    const errorText = await response.text()
    let errorMessage = `API error (${response.status})`
    
    try {
      const errorJson = JSON.parse(errorText)
      errorMessage = errorJson.error || errorMessage
    } catch {
      errorMessage = errorText || errorMessage
    }
    
    throw new Error(errorMessage)
  }
  
  return await response.json()
}

/**
 * Check API health status
 * 
 * @returns {Promise<Object>} Health status
 */
export async function fetchHealth() {
  const url = `${API_BASE_URL}/health`
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`)
  }
  
  return await response.json()
}
