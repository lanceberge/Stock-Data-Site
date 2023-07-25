const mainTab = 'key_statistics'
let fetchedData = {} // Object to store fetched data
const tabs = ['key_statistics', 'balance_sheet', 'earnings', 'cash_flow', 'insider_trading']

async function switchTab (tabId, ticker) {
  await fetchDataForTab(tabId, ticker)

  const tabContents = document.querySelectorAll('.tab-content')
  tabContents.forEach(tabContent => {
    tabContent.classList.remove('active')
  })

  if (fetchedData[tabId].length == 0) {
    document.getElementById("not_found").classList.add('active')
    return
  }

  document.getElementById(tabId).classList.add('active')
  const tabContent = document.getElementById(tabId)
  const tableBody = tabContent.querySelector('tbody')

  tableBody.innerHTML = ''

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

async function search () {
  const ticker = document.getElementById('search_ticker').value
  if (!ticker) {
    return
  }

  const tabNavigation = document.getElementById('tab-navigation')
  tabNavigation.style.display = 'block'

  // reset fetchedData since a new ticker is provided
  fetchedData = {}

  switchTab(mainTab, ticker)
}

async function fetchDataForTab (tabId, ticker) {
  const response = await fetch(`/${tabId}?ticker=${ticker}`)

  const data = await response.json()
  fetchedData[tabId] = data
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
