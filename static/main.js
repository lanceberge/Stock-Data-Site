const mainTab = 'key_statistics'
let activeTab = mainTab
let fetchedData = {}
let ticker
const numberBaseMap = { 2: 'Million', 3: 'Billion', 4: 'Trillion' }

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

  renderTable(tabId)
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

function renderTable (tabId) {
  const tabContent = document.getElementById(tabId)
  tabContent.classList.add('active')
  const data = fetchedData[tabId]

  if (data.Base) {
    const numberBase = data.Base
    const displayedBase = numberBase in numberBaseMap ? 'USD ' + numberBaseMap[numberBase] : ''
    tabContent.querySelector('#number_base').textContent = displayedBase
  }

  for (const table of tabContent.querySelectorAll('table')) {
    for (const row of table.querySelectorAll('tr')) {
      for (const td of row.querySelectorAll('td')) {
        td.remove()
      }

      const key = row.querySelector('th').id
      for (const column of data.Data) {
        const cell = document.createElement('td')
        cell.textContent = column[key]
        row.appendChild(cell)
      }
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
