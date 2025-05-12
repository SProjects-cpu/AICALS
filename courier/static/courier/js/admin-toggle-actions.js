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

  // Add clear actions functionality
  const clearBtn = document.getElementById('clear-actions-btn');
  if (clearBtn) {
    console.log('Clear actions button found');
    
    clearBtn.addEventListener('click', function(e) {
      console.log('Clear actions button clicked');
      e.preventDefault();
      
      if (confirm('Are you sure you want to clear all actions? This cannot be undone.')) {
        try {
          // Try to get CSRF token from the form with ID csrf-form first
          let csrftoken = '';
          const csrfForm = document.getElementById('csrf-form');
          
          if (csrfForm) {
            const csrfInput = csrfForm.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfInput) {
              csrftoken = csrfInput.value;
              console.log('CSRF token found in csrf-form:', csrftoken ? 'Yes (length: ' + csrftoken.length + ')' : 'No');
            } else {
              console.error('CSRF token input not found in csrf-form');
            }
          } else {
            console.error('csrf-form not found');
          }
          
          // If not found in specific form, try general search
          if (!csrftoken) {
            const allCsrfInputs = document.querySelectorAll('[name=csrfmiddlewaretoken]');
            console.log('Found', allCsrfInputs.length, 'CSRF tokens in document');
            
            if (allCsrfInputs.length > 0) {
              csrftoken = allCsrfInputs[0].value;
              console.log('Using first CSRF token found:', csrftoken ? 'Yes (length: ' + csrftoken.length + ')' : 'No');
            }
          }
          
          if (!csrftoken) {
            alert('CSRF token not found. Cannot proceed with clearing actions.');
            return;
          }
          
          // Send AJAX request to clear actions
          console.log('Sending request to /admin/delete_log/?all=true');
          
          fetch('/admin/delete_log/?all=true', {
            method: 'POST',
            headers: {
              'X-CSRFToken': csrftoken,
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            credentials: 'same-origin' // Include cookies
          })
          .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
              throw new Error('Server responded with status: ' + response.status);
            }
            return response.json();
          })
          .then(data => {
            console.log('Response from server:', data);
            
            if (data.status === 'success') {
              // Clear the actions list
              const actionsList = document.querySelector('.actionlist');
              if (actionsList) {
                // Replace with "None available" message
                const parent = actionsList.parentNode;
                actionsList.remove();
                
                const noActions = document.createElement('p');
                noActions.textContent = 'None available';
                parent.appendChild(noActions);
                
                alert(`Successfully cleared ${data.deleted_count} action(s)`);
              } else {
                console.error('Could not find .actionlist element');
                alert('Actions cleared, but UI could not be updated. Please refresh the page.');
              }
            } else {
              alert('Error clearing actions: ' + (data.message || 'Unknown error'));
            }
          })
          .catch(error => {
            console.error('Error during fetch:', error);
            alert('An error occurred while clearing actions: ' + error.message);
          });
        } catch (error) {
          console.error('Exception in clear actions code:', error);
          alert('An error occurred: ' + error.message);
        }
      }
    });
  } else {
    console.error('Clear actions button not found');
  }

  // Debug clear functionality (for developers/admins)
  const debugClearBtn = document.getElementById('debug-clear-btn');
  if (debugClearBtn) {
    debugClearBtn.addEventListener('click', function() {
      console.log('Debug clear button clicked');
      // This would typically connect to a backend API to clear logs
      // For now, just show a message
      alert('Debug clear functionality is active. In production, this would clear debug logs.');
    });
  }
});

// Resize handling for responsive layout
window.addEventListener('resize', function() {
  const recentActionsModule = document.getElementById('recent-actions-module');
  const buttonsContainer = document.querySelector('#recent-actions-module .buttons-container');
  
  if (recentActionsModule && buttonsContainer) {
    // Adjust button container layout based on available width
    if (recentActionsModule.offsetWidth < 500) {
      buttonsContainer.style.flexDirection = 'column';
      buttonsContainer.style.gap = '5px';
    } else {
      buttonsContainer.style.flexDirection = 'row';
      buttonsContainer.style.gap = '10px';
    }
  }
}); 