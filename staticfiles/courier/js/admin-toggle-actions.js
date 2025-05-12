/**
 * Admin Toggle Actions Functionality
 * This script handles the toggling of recent actions in the admin panel
 */
document.addEventListener('DOMContentLoaded', function() {
  console.log('Toggle actions script loaded');
  
  const toggleBtn = document.getElementById('toggle-actions-btn');
  const actionsContent = document.getElementById('actions-content');
  
  console.log('Toggle button:', toggleBtn);
  console.log('Actions content:', actionsContent);
  
  if (!toggleBtn || !actionsContent) {
    console.log('Button or content not found');
    return;
  }
  
  // Force show initially to ensure content is visible and styled correctly
  actionsContent.style.display = 'block';
  
  // Set initial state based on localStorage or default to shown
  const isVisible = localStorage.getItem('actionsVisible') !== 'false'; // Default to visible
  console.log('Initial visibility state:', isVisible);
  
  if (isVisible) {
    actionsContent.classList.add('show');
    toggleBtn.textContent = 'Hide Actions';
  } else {
    actionsContent.classList.remove('show');
    actionsContent.style.display = 'none'; // Ensure it's hidden if not showing
    toggleBtn.textContent = 'Show Actions';
  }
  
  toggleBtn.addEventListener('click', function(e) {
    console.log('Toggle button clicked');
    e.preventDefault(); // Prevent any default button behavior
    
    // Toggle visibility
    const isCurrentlyVisible = actionsContent.classList.contains('show');
    console.log('Currently visible:', isCurrentlyVisible);
    
    if (isCurrentlyVisible) {
      actionsContent.classList.remove('show');
      actionsContent.style.display = 'none';
      toggleBtn.textContent = 'Show Actions';
      localStorage.setItem('actionsVisible', 'false');
    } else {
      actionsContent.classList.add('show');
      actionsContent.style.display = 'block';
      toggleBtn.textContent = 'Hide Actions';
      localStorage.setItem('actionsVisible', 'true');
    }
  });
}); 