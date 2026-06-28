import React from 'react'

/**
 * Jauge circulaire de score de conformité (0-100%).
 * Élément signature de JUMBOSTORE : réapparaît dans le module Analyse DAO
 * et la liste des appels d'offres pour visualiser la compatibilité.
 */
export default function ScoreGauge({ score, size = 88, label }) {
  const value = score ?? 0
  const radius = (size - 10) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference

  let color = '#C0392B'
  if (value >= 80) color = '#2D7D5A'
  else if (value >= 55) color = '#B8762E'

  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#E4E0D8"
            strokeWidth={7}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={7}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
        </svg>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
          }}
        >
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: size * 0.26, color: 'var(--bleu-institutionnel)' }}>
            {Math.round(value)}
          </span>
          <span style={{ fontSize: size * 0.1, color: 'var(--ardoise-clair)', marginTop: -2 }}>/100</span>
        </div>
      </div>
      {label && <span style={{ fontSize: 12.5, color: 'var(--ardoise-clair)', fontWeight: 500 }}>{label}</span>}
    </div>
  )
}
