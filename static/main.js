const mainTab = 'key_statistics'
let activeTab = mainTab
let fetchedData = {}
let ticker
const numberBaseMap = { 2: 'Million', 3: 'Billion', 4: 'Trillion' }

async function displayTab(tabId, period = "yearly") {
  activeTab = tabId

  const tabLinks = document.querySelectorAll('#main_tab_bar .tab-link')
  tabLinks.forEach(tabLink => {
    if (tabLink.getAttribute('data-tab') == tabId) {
      tabLink.classList.add('active')
    } else {
      tabLink.classList.remove('active')
    }
  })

  if (tabId == 'key_statistics') {
    if (!fetchedData[tabId]) {
      const response = await fetch(`/${tabId}?ticker=${ticker}`)
      fetchedData[tabId] = await response.json()
      // TODO handle bad responses

      displayTable(tabId, fetchedData[tabId])
    }
  } else {
    const tabContent = document.getElementById(tabId)
    tabContent.querySelectorAll('#period_tab_bar .tab-link').forEach(tabLink => {
      if (tabLink.getAttribute('data-tab') == period) {
        tabLink.classList.add('active')
      } else {
        tabLink.classList.remove('active')
      }
    })
    
    if (!fetchedData[tabId]) {
      fetchedData[tabId] = {}
    }

    if (!fetchedData[tabId][period]) {
      const response = await fetch(`/${tabId}?ticker=${ticker}&period=${period}`)
      fetchedData[tabId][period] = await response.json()
      // TODO handle bad responses
    }

    const numberBase = fetchedData[tabId][period].Base
    const displayedBase = numberBase in numberBaseMap ? 'USD ' + numberBaseMap[numberBase] : ''
    tabContent.querySelector('#number_base').textContent = displayedBase

    displayTable(tabId, fetchedData[tabId][period])
  }

  const tabContents = document.querySelectorAll('.tab-content')
  tabContents.forEach(tabContent => {
    tabContent.classList.remove('active')
  })

  document.getElementById(tabId).classList.add('active')
}

async function search() {
  const newTicker = document.getElementById('search_bar').value
  if (newTicker == ticker || !newTicker) {
    return
  }

  ticker = newTicker
  fetchedData = {}
  displayTab(mainTab, ticker)
}

function displayTable(tabId, data) {
  const tabContent = document.getElementById(tabId)
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
  const mainTabBar = document.getElementById('main_tab_bar')
  mainTabBar.querySelectorAll('.tab-link').forEach(tabLink => {
    tabLink.addEventListener('click', function () {
      const tabId = tabLink.getAttribute('data-tab')
      displayTab(tabId)
    })
  })

  const periodTabBars = document.querySelectorAll('#period_tab_bar')
  periodTabBars.forEach(periodTabBar => {
    const tabLinks = periodTabBar.querySelectorAll('.tab-link')
    tabLinks.forEach(tabLink => {
      tabLink.addEventListener('click', function () {
        const period = tabLink.getAttribute('data-tab')
        displayTab(activeTab, period)
      })
    })
  })

  const searchInput = document.getElementById('search_bar')
  searchInput.addEventListener('keydown', function (event) {
    if (event.keyCode === 13) {
      search()
    }
  })

  document.addEventListener('keydown', function(event) {
    if (event.key === '/') {
      event.preventDefault();
      document.getElementById('search_bar').focus();
    }
  });
})
