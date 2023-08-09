const mainTab = 'key_statistics'
let activeTab = mainTab
let fetchedData = {}
let ticker
const renderTabMap = {
  key_statistics: renderKeyStatistics,
  balance_sheet: renderBalanceSheet
}

async function switchTab (tabId) {
  if (ticker && !fetchedData[tabId]) {
    await fetchDataForTab(tabId, ticker)
  }

  const tabContents = document.querySelectorAll('.tab-content')
  tabContents.forEach(tabContent => {
    tabContent.classList.remove('active')
  })

  activeTab = tabId
  const tabLinks = document.querySelectorAll('.tab-link')
  tabLinks.forEach(link => {
    if (link.getAttribute('data-tab') == tabId) {
      link.classList.add('active')
    } else {
      link.classList.remove('active')
    }
  })

  if (fetchedData[tabId].length == 0) {
    document.getElementById('not_found').classList.add('active')
    return
  }

  if (tabId in renderTabMap) {
    renderTabMap[tabId]()
  }
}

async function search () {
  ticker = document.getElementById('search_ticker').value
  if (!ticker) {
    return
  }

  // reset fetchedData since a new ticker is provided
  fetchedData = {}

  switchTab(activeTab, ticker)
}

function renderKeyStatistics () {
  const tabContent = document.getElementById('key_statistics')
  tabContent.classList.add('active')

  const table = tabContent.querySelector('table')
  const data = fetchedData.key_statistics
  for (const key in data) {
    const th = table.querySelector(`th[id="${key}"]`)

    if (th) {
      const td = th.nextElementSibling
      td.textContent = data[key]
    }
  }
}

function renderBalanceSheet () {
  const tabContent = document.getElementById('balance_sheet')
  tabContent.classList.add('active')

  const data = fetchedData.balance_sheet

  // TODO display the base

  // TODO for each table in tabContent
  for (const row of tabContent.querySelectorAll('#current_assets tr')) {
    for (const td of row.querySelectorAll('td')) {
      td.remove()
    }
    const key = row.querySelector('th').textContent

    for (const column of data) {
      const cell = document.createElement('td')
      cell.textContent = column[key]
      row.appendChild(cell)
    }
  }
}

async function fetchDataForTab (tabId, ticker) {
  const response = await fetch(`/${tabId}?ticker=${ticker}`)

  const data = await response.json()
  fetchedData[tabId] = data
}

document.addEventListener('DOMContentLoaded', function () {
  const tabLinks = document.querySelectorAll('#tab_navigation .tab-link')

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
