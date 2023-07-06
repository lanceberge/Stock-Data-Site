function switchTab (tabId) {
    // Get all tab content elements
    const tabs = document.getElementsByClassName('tab');

    // Remove active class from all tab content elements
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }

  // Add active class to the selected tab content element
    document.getElementById(tabId).classList.add('active');
}

function search () {
    const query = document.getElementById('searchInput').value;
    // switchTab('tab1');

    const tabNavigation = document.getElementById('tab-navigation');
    tabNavigation.style.display = 'block';
}
