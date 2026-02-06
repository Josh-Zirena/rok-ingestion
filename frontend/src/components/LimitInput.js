/**
 * Limit input component
 */

import { appState } from '../state.js'

export class LimitInput {
  constructor(containerId) {
    this.container = document.getElementById(containerId)
    this.render()
    this.attachListeners()
  }
  
  render() {
    const state = appState.get()
    
    this.container.innerHTML = `
      <div class="control-group">
        <label for="limit-input">Limit:</label>
        <input 
          type="number" 
          id="limit-input" 
          value="${state.limit}" 
          min="1" 
          max="500"
          step="10"
        >
        <span class="help-text">Max 500</span>
      </div>
    `
  }
  
  attachListeners() {
    const input = this.container.querySelector('#limit-input')
    
    input.addEventListener('input', (e) => {
      let value = parseInt(e.target.value, 10)
      
      // Clamp value between 1 and 500
      if (value < 1) value = 1
      if (value > 500) value = 500
      
      appState.set({ limit: value })
    })
    
    input.addEventListener('blur', (e) => {
      // Ensure valid value on blur
      let value = parseInt(e.target.value, 10)
      if (isNaN(value) || value < 1) {
        value = 1
        e.target.value = value
      } else if (value > 500) {
        value = 500
        e.target.value = value
      }
      appState.set({ limit: value })
    })
  }
}
