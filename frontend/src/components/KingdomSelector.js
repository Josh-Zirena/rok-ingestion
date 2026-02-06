/**
 * Kingdom selector component
 */

import { appState } from '../state.js'

export class KingdomSelector {
  constructor(containerId) {
    this.container = document.getElementById(containerId)
    this.render()
    this.attachListeners()
  }
  
  render() {
    const state = appState.get()
    const showWarning = state.kingdom !== '3951' && state.kingdom !== ''
    
    this.container.innerHTML = `
      <div class="control-group">
        <label for="kingdom-input">Kingdom:</label>
        <input 
          type="text" 
          id="kingdom-input" 
          placeholder="Enter kingdom ID" 
          value="${state.kingdom}"
          pattern="[0-9]{1,6}"
          title="Kingdom ID must be 1-6 digits"
        >
        <span class="help-text">Default: 3951</span>
        ${showWarning ? '<span class="kingdom-warning">⚠️ Warning: Only Kingdom 3951 has verified data</span>' : ''}
      </div>
    `
  }
  
  attachListeners() {
    const input = this.container.querySelector('#kingdom-input')
    
    input.addEventListener('input', (e) => {
      const value = e.target.value.trim()
      appState.set({ kingdom: value })
      this.render()
      this.attachListeners()
    })
    
    input.addEventListener('blur', (e) => {
      // Validate on blur
      const value = e.target.value.trim()
      if (value && !/^[0-9]{1,6}$/.test(value)) {
        e.target.classList.add('invalid')
      } else {
        e.target.classList.remove('invalid')
      }
    })
  }
}
