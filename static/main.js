const mainTab = 'key_statistics'
let activeTab = mainTab
let fetchedData = {}
let ticker
const numberBaseMap = { 2: 'Million', 3: 'Billion', 4: 'Trillion' }
const Period = { Quartely: 'quarter', Yearly: 'yearly' }

async function displayTab (tabId) {
  activeTab = tabId

  // TODO display not_found tab based on bad responses
  if (tabId == 'key_statistics') {
    if (!fetchedData[tabId]) {
      const response = await fetch(`/${tabId}?ticker=${ticker}`)
      fetchedData[tabId] = await response.json()
    }
  } else {
    // TODO period stuff
    if (!fetchedData[tabId]) {
      const response = await fetch(`/${tabId}?ticker=${ticker}`)
      fetchedData[tabId] = await response.json()
    }

    const numberBase = fetchedData[tabId].Base
    const displayedBase = numberBase in numberBaseMap ? 'USD ' + numberBaseMap[numberBase] : ''
    const tabContent = document.getElementById(tabId)
    tabContent.querySelector('#number_base').textContent = displayedBase
  }

  const tabContents = document.querySelectorAll('.tab-content')
  tabContents.forEach(tabContent => {
    tabContent.classList.remove('active')
  })

  displayTable(tabId)
  document.getElementById(tabId).classList.add('active')
}

async function search () {
  ticker = document.getElementById('search_ticker').value

  // TODO keep track of invalid tickers
  if (!ticker) {
    return
  }

  // reset fetchedData since a new ticker is provided
  fetchedData = {}

  displayTab(activeTab, ticker)
}

function displayTable (tabId) {
  const tabContent = document.getElementById(tabId)
  const data = fetchedData[tabId]

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

document.addEventListener('DOMContentLoaded', function () {
  const tabNavigationBars = document.querySelectorAll('.tab-navigation')

  tabNavigationBars.forEach(tabNavigationBar => {
    const tabLinks = tabNavigationBar.querySelectorAll('.tab-link')
    tabLinks.forEach(tabLink => {
      tabLink.addEventListener('click', function () {
        tabLinks.forEach(link => {
          link.classList.remove('active')
        })
        tabLink.classList.add('active')
      })
    })
  })

  const mainTabBar = document.getElementById('main_tab_bar')
  mainTabBar.querySelectorAll('.tab-link').forEach(tabLink => {
    tabLink.addEventListener('click', function () {
      const tabId = tabLink.getAttribute('data-tab')
      displayTab(tabId)
    })
  })

  const searchInput = document.getElementById('search_ticker')
  searchInput.addEventListener('keydown', function (event) {
    if (event.keyCode === 13) {
      search()
    }
  })
})
