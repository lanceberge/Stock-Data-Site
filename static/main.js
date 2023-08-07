const mainTab = 'key_statistics'
let activeTab = mainTab
let fetchedData = {}
let ticker

async function switchTab (tabId) {
  if (ticker) {
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

  // TODO set up data for other tabs
  if (tabId == 'key_statistics') {
    const tabContent = document.getElementById(tabId)
    tabContent.classList.add('active')

    const table = tabContent.querySelector('table')
    const data = fetchedData[tabId]
    for (const key in data) {
      const th = table.querySelector(`th[id="${key}"]`) // Select the th with the specified id (key)

      if (th) {
        const td = th.nextElementSibling
        td.textContent = data[key]
      }
    }
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
