import './FilterTabs.css'

export function FilterTabs({ activeFilter, onFilterChange, counts = {} }) {
  const tabs = [
    { key: 'all', label: 'Todos', count: counts.all },
    { key: 'active', label: 'Activos', count: counts.active },
    { key: 'inactive', label: 'Inactivos', count: counts.inactive },
    { key: 'basic', label: 'Básicos', count: counts.basic },
  ]

  return (
    <div className="filterTabsContainer">
      {tabs.map((tab) => {
        const isActive = activeFilter === tab.key
        const buttonClass = isActive ? 'filterTabButtonActive' : 'filterTabButton'

        return (
          <button
            key={tab.key}
            type="button"
            onClick={() => onFilterChange(tab.key)}
            className={`filterTabBase ${buttonClass}`}
          >
            <span className="filterTabLabel">{tab.label}</span>
            {tab.count !== undefined && (
              <span className={`filterTabCount ${isActive ? 'filterTabCountActive' : ''}`}>
                {tab.count}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
