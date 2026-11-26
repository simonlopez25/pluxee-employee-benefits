import './Icon.css'

export function Icon({ name, size = 20, className = '' }) {
  const iconProps = {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 2,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    className: `iconSvg ${className}`.trim(),
  }

  switch (name) {
    case 'restaurant':
    case 'comida':
      return (
        <svg {...iconProps}>
          <path d="M18 2v6a3 3 0 0 1-3 3 3 3 0 0 1-3-3V2" />
          <path d="M15 2v10" />
          <path d="M15 12v10" />
          <path d="M6 2v20" />
          <path d="M6 2a4 4 0 0 1 4 4c0 2-2 3-4 3" />
        </svg>
      )
    case 'transport':
    case 'transporte':
      return (
        <svg {...iconProps}>
          <path d="M8 6v6" />
          <path d="M16 6v6" />
          <path d="M4 12h16" />
          <rect x="4" y="3" width="16" height="16" rx="2" />
          <path d="M6 19v2" />
          <path d="M18 19v2" />
        </svg>
      )
    case 'training':
    case 'formacion':
    case 'formación':
      return (
        <svg {...iconProps}>
          <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
          <path d="M6 12v5c3 3 9 3 12 0v-5" />
        </svg>
      )
    case 'health':
    case 'salud':
      return (
        <svg {...iconProps}>
          <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
          <path d="M12 9v4" />
          <path d="M10 11h4" />
        </svg>
      )
    case 'daycare':
    case 'guarderia':
    case 'guardería':
      return (
        <svg {...iconProps}>
          <circle cx="12" cy="12" r="9" />
          <path d="M9 10h.01" />
          <path d="M15 10h.01" />
          <path d="M8 14s1.5 2 4 2 4-2 4-2" />
          <path d="M12 3a3 3 0 0 1 3 3" />
        </svg>
      )
    case 'plus':
      return (
        <svg {...iconProps}>
          <path d="M5 12h14" />
          <path d="M12 5v14" />
        </svg>
      )
    case 'edit':
      return (
        <svg {...iconProps}>
          <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
          <path d="m15 5 4 4" />
        </svg>
      )
    case 'close':
      return (
        <svg {...iconProps}>
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      )
    case 'check':
      return (
        <svg {...iconProps}>
          <path d="M20 6 9 17l-5-5" />
        </svg>
      )
    case 'catalog':
    case 'box':
      return (
        <svg {...iconProps}>
          <path d="m7.5 4.27 9 5.15" />
          <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
          <path d="m3.3 7 8.7 5 8.7-5" />
          <path d="M12 22V12" />
        </svg>
      )
    case 'dashboard':
      return (
        <svg {...iconProps}>
          <rect width="7" height="7" x="3" y="3" rx="1.5" />
          <rect width="7" height="7" x="14" y="3" rx="1.5" />
          <rect width="7" height="7" x="14" y="14" rx="1.5" />
          <rect width="7" height="7" x="3" y="14" rx="1.5" />
        </svg>
      )
    case 'groups':
    case 'users':
      return (
        <svg {...iconProps}>
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      )
    case 'employee':
      return (
        <svg {...iconProps}>
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      )
    case 'budget':
    case 'piggyBank':
      return (
        <svg {...iconProps}>
          <path d="M19 5c-1.5 0-2.8 1.4-3 2-3.5-1.5-11-.3-11 5 0 1.8.8 3.5 2 4.5V19h3v-1h4v1h3v-2.8c2.4-1.2 3.8-3.5 3.8-5.2 0-1.5-.8-3-1.8-3" />
          <path d="M2 9v1a2 2 0 0 0 2 2h1" />
          <path d="M10 5.5V7" />
          <path d="M14 11h.01" />
        </svg>
      )
    case 'assignments':
      return (
        <svg {...iconProps}>
          <rect width="8" height="4" x="8" y="2" rx="1" />
          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
          <path d="M9 12h6" />
          <path d="M9 16h6" />
        </svg>
      )
    case 'expenses':
      return (
        <svg {...iconProps}>
          <rect width="20" height="14" x="2" y="5" rx="2" />
          <path d="M12 9v6" />
          <path d="M10 10.5h3.5a1 1 0 0 1 0 2H10.5a1 1 0 0 0 0 2H14" />
        </svg>
      )
    case 'switchUser':
      return (
        <svg {...iconProps}>
          <path d="M4 17h16" />
          <path d="m16 13 4 4-4 4" />
          <path d="M20 7H4" />
          <path d="m8 11-4-4 4-4" />
        </svg>
      )
    case 'calendar':
      return (
        <svg {...iconProps}>
          <rect width="18" height="18" x="3" y="4" rx="2" />
          <path d="M16 2v4" />
          <path d="M8 2v4" />
          <path d="M3 10h18" />
        </svg>
      )
    case 'chevronLeft':
      return (
        <svg {...iconProps}>
          <path d="m15 18-6-6 6-6" />
        </svg>
      )
    case 'chevronRight':
      return (
        <svg {...iconProps}>
          <path d="m9 18 6-6-6-6" />
        </svg>
      )
    case 'info':
      return (
        <svg {...iconProps}>
          <circle cx="12" cy="12" r="10" />
          <path d="M12 16v-4" />
          <path d="M12 8h.01" />
        </svg>
      )
    case 'wallet':
      return (
        <svg {...iconProps}>
          <path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1" />
          <path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4" />
        </svg>
      )
    case 'alert':
    case 'warning':
      return (
        <svg {...iconProps}>
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
          <path d="M12 9v4" />
          <path d="M12 17h.01" />
        </svg>
      )
      case 'gift':
        return (
          <svg {...iconProps}>
            <rect x="3" y="8" width="18" height="4" rx="1" />
            <path d="M12 8v13" />
            <path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7" />
            <path d="M7.5 8a2.5 2.5 0 0 1 0-5C9 3 12 5.5 12 8" />
            <path d="M16.5 8a2.5 2.5 0 0 0 0-5C15 3 12 5.5 12 8" />
          </svg>
      )
      case 'home':
      return (
        <svg {...iconProps}>
          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
          <path d="M9 22V12h6v10" />
        </svg>
      )
    case 'history':
      return (
        <svg {...iconProps}>
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
          <path d="M3 3v5h5" />
          <path d="M12 7v5l4 2" />
        </svg>
      )
    case 'spinner':
      return (
        <svg {...iconProps} className={`iconSvg iconSpin ${className}`.trim()}>
          <path d="M21 12a9 9 0 1 1-6.219-8.56" />
        </svg>
      )
    default:
      return (
        <svg {...iconProps}>
          <circle cx="12" cy="12" r="10" />
          <line x1="12" x2="12" y1="8" y2="12" />
          <line x1="12" x2="12.01" y1="16" y2="16" />
        </svg>
      )
  }
}