import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import './MonthSelector.css'

const MONTH_NAMES = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

export function MonthSelector({ selectedPeriod, onPeriodChange }) {
  const currentDate = new Date(selectedPeriod)
  const year = currentDate.getFullYear()
  const monthIndex = currentDate.getMonth()

  const formattedMonth = `${MONTH_NAMES[monthIndex]} ${year}`

  const handlePrevMonth = () => {
    const prevDate = new Date(year, monthIndex - 1, 1)
    const y = prevDate.getFullYear()
    const m = String(prevDate.getMonth() + 1).padStart(2, '0')
    onPeriodChange(`${y}-${m}-01`)
  }

  const handleNextMonth = () => {
    const nextDate = new Date(year, monthIndex + 1, 1)
    const y = nextDate.getFullYear()
    const m = String(nextDate.getMonth() + 1).padStart(2, '0')
    onPeriodChange(`${y}-${m}-01`)
  }

  const handleCurrentMonth = () => {
    const now = new Date()
    const y = now.getFullYear()
    const m = String(now.getMonth() + 1).padStart(2, '0')
    onPeriodChange(`${y}-${m}-01`)
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
