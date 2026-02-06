/**
 * Date selector component with "Use Latest" option
 */

import { appState } from '../state.js'

export class DateSelector {
  constructor(containerId) {
    this.container = document.getElementById(containerId)
    this.render()
    this.attachListeners()
  }
  
  render() {
    const state = appState.get()
    
    this.container.innerHTML = `
      <div class="control-group">
        <label for="dt-input">Date:</label>
        <input 
          type="date" 
          id="dt-input" 
          ${state.useLatest ? 'disabled' : ''}
          value="${state.useLatest ? '' : state.dt}"
        >
        <label class="checkbox-label">
          <input type="checkbox" id="use-latest-checkbox" ${state.useLatest ? 'checked' : ''}> 
          Use Latest
        </label>
        <span class="help-text">Or select a specific snapshot date</span>
      </div>
    `
  }
  
  attachListeners() {
    const dateInput = this.container.querySelector('#dt-input')
    const checkbox = this.container.querySelector('#use-latest-checkbox')
    
    checkbox.addEventListener('change', (e) => {
      const useLatest = e.target.checked
      dateInput.disabled = useLatest
      
      appState.set({ 
        useLatest,
        dt: useLatest ? 'latest' : dateInput.value 
      })
      
      if (!useLatest && !dateInput.value) {
        dateInput.focus()
      }
    })
    
    dateInput.addEventListener('change', (e) => {
      if (!checkbox.checked) {
        appState.set({ dt: e.target.value })
      }
    })
  }
}
