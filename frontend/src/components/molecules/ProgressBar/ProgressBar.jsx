import './ProgressBar.css'

export function ProgressBar({ value = 0, max = 100, showLabel = true }) {
  const numericValue = typeof value === 'number' ? value : parseFloat(value) || 0
  const percentage = max > 0 ? (numericValue / max) * 100 : 0
  const clampedPercent = Math.min(Math.max(percentage, 0), 100)

  let statusClass = 'progressNormal'
  if (clampedPercent > 90) {
    statusClass = 'progressDanger'
  } else if (clampedPercent > 75) {
    statusClass = 'progressWarning'
  }

  const formattedPercentage = numericValue.toLocaleString('es-ES', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  })

  return (
    <div className="progressBarContainer">
      <div className="progressBarTrack">
        <svg
          className="progressBarSvg"
          viewBox="0 0 100 6"
          preserveAspectRatio="none"
        >
          <rect className="progressSvgBg" x="0" y="0" width="100" height="6" rx="3" />
          <rect
            className={`progressSvgFill ${statusClass}`}
            x="0"
            y="0"
            width={clampedPercent}
            height="6"
            rx="3"
          />
        </svg>
      </div>
      {showLabel && (
        <span className={`progressLabel ${statusClass}`}>
          {formattedPercentage}%
        </span>
      )}
    </div>
  )
}
