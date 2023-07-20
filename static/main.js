const mainTab = 'key_statistics'

function switchTab (tabId) {
  const tabContents = document.querySelectorAll('.tab-content')
  tabContents.forEach(tabContent => {
    tabContent.classList.remove('active')
  })

  // const tabs = document.getElementsByClassName('tab-content')
  document.getElementById(tabId).classList.add('active')
}

document.addEventListener('DOMContentLoaded', function () {
  const tabLinks = document.querySelectorAll('.tab-link')

  tabLinks.forEach(tabLink => {
    tabLink.addEventListener('click', function () {
      const tabId = this.getAttribute('data-tab')
      switchTab(tabId)
    })
  })
})

function search () {
  const query = document.getElementById('searchInput').value

  switchTab(mainTab)
  const tabNavigation = document.getElementById('tab-navigation')
  tabNavigation.style.display = 'block'
}

const fetchedData = {} // Object to store fetched data

async function fetchDataForTab (tabId) {
  const response = await fetch(`/${tabId}`)
  const data = await response.json()
  fetchedData[tabId] = data // Save fetched data to the object
  updateTabContent(tabId)
}

function updateTabContent (tabId) {
  const tabContent = document.getElementById(tabId)
  const tableBody = tabContent.querySelector('tbody')

  // Clear existing table rows
  tableBody.innerHTML = ''

  // Append new data to the table
  fetchedData[tabId].forEach(row => {
    const tableRow = document.createElement('tr')
    tableRow.innerHTML = `
          <td>${row[0]}</td>
          <td>${row[1]}</td>
          <td>${row[2]}</td>
          <td>${row[3]}</td>
        `
    tableBody.appendChild(tableRow)
  })
}

document.addEventListener('DOMContentLoaded', function () {
  const tabs = document.querySelectorAll('.tab-link')
  tabs.forEach(tab => {
    tab.addEventListener('click', function () {
      const tabId = this.getAttribute('data-tab')
      if (!fetchedData[tabId]) {
        fetchDataForTab(tabId)
      } else {
        updateTabContent(tabId)
      }
    })
  })
})
