/**
 * Leaderboard table component
 */

import { appState } from '../state.js'

export class LeaderboardTable {
  constructor(containerId) {
    this.container = document.getElementById(containerId)
    this.setupStateListener()
  }
  
  setupStateListener() {
    // Subscribe to state changes
    appState.subscribe((state) => {
      if (state.loading) {
        this.renderLoading()
      } else if (state.error) {
        this.renderError(state.error)
      } else if (state.leaderboardData) {
        this.renderLeaderboard(state.leaderboardData)
      }
    })
  }
  
  renderLeaderboard(data) {
    if (!data.rows || data.rows.length === 0) {
      this.container.innerHTML = `
        <div class="empty-state">
          <p>No data available for this query.</p>
        </div>
      `
      return
    }
    
    const metricLabel = this.getMetricLabel(data.metric)
    
    this.container.innerHTML = `
      <div class="leaderboard">
        <div class="leaderboard-header">
          <h2>Top ${data.rows.length} by ${metricLabel}</h2>
          <p class="metadata">Kingdom ${data.kingdom} • ${data.dt}</p>
        </div>
        
        <table class="leaderboard-table">
          <thead>
            <tr>
              <th class="rank">#</th>
              <th class="id">ID</th>
              <th class="name">Name</th>
              <th class="alliance">Alliance</th>
              <th class="value">${metricLabel}</th>
            </tr>
          </thead>
          <tbody>
            ${data.rows.map((row, index) => this.renderRow(row, index + 1)).join('')}
          </tbody>
        </table>
      </div>
    `
  }
  
  renderRow(row, rank) {
    const rankClass = rank <= 3 ? `rank-${rank}` : ''
    
    return `
      <tr class="${rankClass}">
        <td class="rank">${rank}</td>
        <td class="id">${this.escapeHtml(row.id || '-')}</td>
        <td class="name">${this.escapeHtml(row.name || 'Unknown')}</td>
        <td class="alliance">${this.escapeHtml(row.alliance || '-')}</td>
        <td class="value">${this.formatNumber(row.value)}</td>
      </tr>
    `
  }
  
  renderLoading() {
    this.container.innerHTML = `
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading leaderboard...</p>
      </div>
    `
  }
  
  renderError(message) {
    this.container.innerHTML = `
      <div class="error-state">
        <h3>Error Loading Leaderboard</h3>
        <p>${this.escapeHtml(message)}</p>
        <p>Please check your parameters and try again.</p>
      </div>
    `
  }
  
  getMetricLabel(metric) {
    const labels = {
      power: 'Power',
      killpoints: 'Kill Points',
      kills: 'Total Kills',
      deads: 'Deaths',
    }
    return labels[metric] || metric
  }
  
  formatNumber(num) {
    if (num == null || isNaN(num)) return '-'
    return num.toLocaleString('en-US')
  }
  
  escapeHtml(str) {
    if (str == null) return ''
    const div = document.createElement('div')
    div.textContent = str
    return div.innerHTML
  }
}

