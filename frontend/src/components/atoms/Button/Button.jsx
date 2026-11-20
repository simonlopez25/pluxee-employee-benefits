import './Button.css'

export function Button({
  type = 'button',
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  children,
  className = '',
  icon,
}) {
  const variantClassMap = {
    primary: 'buttonPrimary',
    secondary: 'buttonSecondary',
    outline: 'buttonOutline',
    ghost: 'buttonGhost',
    danger: 'buttonDanger',
  }

  const sizeClassMap = {
    sm: 'buttonSm',
    md: 'buttonMd',
    lg: 'buttonLg',
  }

  const variantClass = variantClassMap[variant] || 'buttonPrimary'
  const sizeClass = sizeClassMap[size] || 'buttonMd'

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`buttonBase ${variantClass} ${sizeClass} ${className}`.trim()}
    >
      {icon && <span className="buttonIconWrapper">{icon}</span>}
      <span className="buttonLabel">{children}</span>
    </button>
  )
}
