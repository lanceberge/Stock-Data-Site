const mainTab = 'key_statistics'
let fetchedData = {} // Object to store fetched data
const tabs = ['key_statistics', 'balance_sheet', 'earnings', 'cash_flow', 'insider_trading']

function switchTab (tabId) {
  const tabContents = document.querySelectorAll('.tab-content')
  tabContents.forEach(tabContent => {
    tabContent.classList.remove('active')
  })

  document.getElementById(tabId).classList.add('active')
  updateTabContent(tabId)
}

async function search () {
  const tabNavigation = document.getElementById('tab-navigation')
  tabNavigation.style.display = 'block'

  fetchedData = {}

  const ticker = document.getElementById('search_ticker').value

  await fetchDataForTab(mainTab, ticker)
  switchTab(mainTab)

  tabs.slice(1).forEach(tabId => {
    fetchDataForTab(tabId, ticker)
  })
}

async function fetchDataForTab (tabId, ticker) {
  const response = await fetch(`/${tabId}?ticker=${ticker}`)
  const data = await response.json()
  fetchedData[tabId] = data
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
  const tabLinks = document.querySelectorAll('.tab-link')

  tabLinks.forEach(tabLink => {
    tabLink.addEventListener('click', function () {
      const tabId = this.getAttribute('data-tab')
      switchTab(tabId)
    })
  })

  const searchInput = document.getElementById('search_ticker')
  searchInput.addEventListener('keydown', function (event) {
    if (event.keyCode === 13) {
      search()
    }
  })
})
