import './Badge.css'

export function Badge({ variant = 'default', children, className = '' }) {
  const variantClassMap = {
    default: 'badgeDefault',
    basic: 'badgeBasic',
    active: 'badgeActive',
    inactive: 'badgeInactive',
  }

  const selectedClass = variantClassMap[variant] || 'badgeDefault'

  return (
    <span className={`badgeBase ${selectedClass} ${className}`.trim()}>
      {children}
    </span>
  )
}

