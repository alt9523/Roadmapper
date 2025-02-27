// Navigation utilities

// Navigation stack to track user's path through the application
const navStack = [];

/**
 * Go back to the previous view
 */
function goBack() {
  if (navStack.length > 0) {
    navStack.pop(); // Remove current view
    
    // Show the previous view or main view if stack is empty
    const previousView = navStack.length > 0 ? navStack[navStack.length - 1] : 'mainView';
    
    // Hide all views
    document.querySelectorAll('[id$="View"]').forEach(el => {
      el.style.display = 'none';
    });
    
    // Show the previous view
    document.getElementById(previousView).style.display = 'block';
  }
}

/**
 * Show the main view
 */
function showMainView() {
  // Clear navigation stack
  navStack.length = 0;
  
  // Hide all views
  document.querySelectorAll('[id$="View"]').forEach(el => {
    el.style.display = 'none';
  });
  
  // Show main view
  document.getElementById('mainView').style.display = 'block';
}

module.exports = {
  navStack,
  goBack,
  showMainView
}; 