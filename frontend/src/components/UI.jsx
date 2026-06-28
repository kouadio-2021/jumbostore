import React from 'react'

export function Card({ children, style, className = '', onClick }) {
  return (
    <div
      className={`ui-card ${className}`}
      onClick={onClick}
      style={{
        background: 'var(--fond-blanc)',
        border: '1px solid var(--bordure)',
        borderRadius: 'var(--rayon-lg)',
        boxShadow: 'var(--ombre-sm)',
        ...style,
      }}
    >
      {children}
    </div>
  )
}

export function PageHeader({ eyebrow, title, subtitle, action }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 16, marginBottom: 28 }}>
      <div>
        {eyebrow && (
          <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--or-accent)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 6 }}>
            {eyebrow}
          </div>
        )}
        <h1 style={{ fontSize: 28, lineHeight: 1.2 }}>{title}</h1>
        {subtitle && <p style={{ color: 'var(--ardoise-clair)', marginTop: 6, fontSize: 14.5, maxWidth: 640 }}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}

export function EmptyState({ icon: Icon, title, description }) {
  return (
    <div style={{ textAlign: 'center', padding: '64px 24px', color: 'var(--ardoise-clair)' }}>
      {Icon && <Icon size={36} style={{ marginBottom: 14, opacity: 0.5 }} />}
      <div style={{ fontWeight: 600, color: 'var(--ardoise)', fontSize: 15.5, marginBottom: 4 }}>{title}</div>
      {description && <div style={{ fontSize: 13.5 }}>{description}</div>}
    </div>
  )
}

export function Loader({ label = 'Chargement…' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '40px 0', color: 'var(--ardoise-clair)', fontSize: 14 }}>
      <span className="ui-spinner" />
      {label}
    </div>
  )
}

export function PrimaryButton({ children, onClick, disabled, type = 'button', style }) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{
        background: disabled ? '#B7C3CC' : 'var(--bleu-institutionnel)',
        color: '#fff',
        padding: '11px 20px',
        borderRadius: 8,
        fontWeight: 600,
        fontSize: 14,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        opacity: disabled ? 0.7 : 1,
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'background 0.15s ease',
        ...style,
      }}
    >
      {children}
    </button>
  )
}

export function SecondaryButton({ children, onClick, disabled, style }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        background: 'transparent',
        color: 'var(--bleu-institutionnel)',
        padding: '10px 18px',
        borderRadius: 8,
        fontWeight: 600,
        fontSize: 14,
        border: '1.5px solid var(--bleu-institutionnel)',
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        opacity: disabled ? 0.5 : 1,
        cursor: disabled ? 'not-allowed' : 'pointer',
        ...style,
      }}
    >
      {children}
    </button>
  )
}
