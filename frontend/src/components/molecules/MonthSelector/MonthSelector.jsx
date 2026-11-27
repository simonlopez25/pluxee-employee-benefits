import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon/Icon'
import { MONTH_NAMES_CAPITALIZED, firstDayOfMonth } from '../../../utils/dates'
import './MonthSelector.css'

export function MonthSelector({ selectedPeriod, onPeriodChange }) {
  const currentDate = new Date(selectedPeriod)
  const year = currentDate.getFullYear()
  const monthIndex = currentDate.getMonth()

  const formattedMonth = `${MONTH_NAMES_CAPITALIZED[monthIndex]} ${year}`

  const handlePrevMonth = () => {
    const prevDate = new Date(year, monthIndex - 1, 1)
    onPeriodChange(firstDayOfMonth(prevDate))
  }

  const handleNextMonth = () => {
    const nextDate = new Date(year, monthIndex + 1, 1)
    onPeriodChange(firstDayOfMonth(nextDate))
  }

  const handleCurrentMonth = () => {
    onPeriodChange(firstDayOfMonth())
  }

  const now = new Date()
  const isCurrentMonth =
    now.getFullYear() === year && now.getMonth() === monthIndex

  return (
    <div className="monthSelectorContainer">
      <div className="monthSelectorControls">
        <button
          type="button"
          onClick={handlePrevMonth}
          className="monthNavButton"
          aria-label="Mes anterior"
        >
          <Icon name="chevronLeft" size={16} />
        </button>

        <div className="monthDisplay">
          <Icon name="calendar" size={16} className="monthCalendarIcon" />
          <span className="monthLabel">{formattedMonth}</span>
        </div>

        <button
          type="button"
          onClick={handleNextMonth}
          className="monthNavButton"
          aria-label="Mes siguiente"
        >
          <Icon name="chevronRight" size={16} />
        </button>
      </div>

      {!isCurrentMonth && (
        <Button
          variant="outline"
          size="sm"
          onClick={handleCurrentMonth}
          className="monthTodayButton"
        >
          Mes actual
        </Button>
      )}
    </div>
  )
}
