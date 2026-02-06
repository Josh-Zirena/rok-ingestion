/**
 * Metric selector component
 */

import { appState } from '../state.js'

const METRICS = [
  { value: 'power', label: 'Power' },
  { value: 'killpoints', label: 'Kill Points' },
  { value: 'kills', label: 'Total Kills' },
  { value: 'deads', label: 'Deaths' },
]

export class MetricSelector {
  constructor(containerId) {
    this.container = document.getElementById(containerId)
    this.render()
    this.attachListeners()
  }
  
  render() {
    const state = appState.get()
    
    const options = METRICS.map(metric => `
      <option value="${metric.value}" ${state.metric === metric.value ? 'selected' : ''}>
        ${metric.label}
      </option>
    `).join('')
    
    this.container.innerHTML = `
      <div class="control-group">
        <label for="metric-select">Metric:</label>
        <select id="metric-select">
          ${options}
        </select>
      </div>
    `
  }
  
  attachListeners() {
    const select = this.container.querySelector('#metric-select')
    
    select.addEventListener('change', (e) => {
      appState.set({ metric: e.target.value })
    })
  }
}
