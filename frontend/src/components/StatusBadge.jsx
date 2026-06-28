import React from 'react'

const STYLES = {
  // Statuts appels d'offres
  nouveau: { bg: '#E7F0F7', color: '#0E3A5C', label: 'Nouveau' },
  en_analyse: { bg: '#FAF1E3', color: '#B8762E', label: 'En analyse' },
  en_preparation: { bg: '#EFEAF7', color: '#5B3FA0', label: 'En préparation' },
  soumis: { bg: '#E2EEF9', color: '#1B5680', label: 'Soumis' },
  gagne: { bg: '#E7F3EC', color: '#2D7D5A', label: 'Marché gagné' },
  perdu: { bg: '#FBEAE8', color: '#C0392B', label: 'Marché perdu' },
  archive: { bg: '#F1EFEA', color: '#6B7280', label: 'Archivé' },
  // Conformité
  Conforme: { bg: '#E7F3EC', color: '#2D7D5A', label: 'Conforme' },
  'Conforme avec réserves': { bg: '#FAF1E3', color: '#B8762E', label: 'Conforme avec réserves' },
  'Non conforme': { bg: '#FBEAE8', color: '#C0392B', label: 'Non conforme' },
  // Soumissions
  brouillon: { bg: '#F1EFEA', color: '#6B7280', label: 'Brouillon' },
  en_cours: { bg: '#FAF1E3', color: '#B8762E', label: 'En cours' },
  complete: { bg: '#E2EEF9', color: '#1B5680', label: 'Complète' },
  validee: { bg: '#E7F3EC', color: '#2D7D5A', label: 'Validée' },
  deposee: { bg: '#EFEAF7', color: '#5B3FA0', label: 'Déposée' },
  // Factures
  envoye: { bg: '#E2EEF9', color: '#1B5680', label: 'Envoyé' },
  paye: { bg: '#E7F3EC', color: '#2D7D5A', label: 'Payé' },
  en_retard: { bg: '#FBEAE8', color: '#C0392B', label: 'En retard' },
  annule: { bg: '#F1EFEA', color: '#6B7280', label: 'Annulé' },
  // Documents entreprise
  valide: { bg: '#E7F3EC', color: '#2D7D5A', label: 'Valide' },
  expire: { bg: '#FBEAE8', color: '#C0392B', label: 'Expiré' },
  manquant: { bg: '#FBEAE8', color: '#C0392B', label: 'Manquant' },
}

export default function StatusBadge({ status }) {
  const style = STYLES[status] || { bg: '#F1EFEA', color: '#6B7280', label: status }
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '4px 11px',
        borderRadius: 20,
        fontSize: 12.5,
        fontWeight: 600,
        background: style.bg,
        color: style.color,
        whiteSpace: 'nowrap',
      }}
    >
      {style.label}
    </span>
  )
}
