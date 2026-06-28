import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Calendar, Building, ChevronRight } from 'lucide-react'
import { getAppelsOffres } from '../services/api.js'
import { Card, PageHeader, Loader, EmptyState } from '../components/UI.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

const CATEGORIES = ['BTP', 'Informatique', 'Fournitures', 'Électricité', 'Hydraulique', 'Sécurité', 'Transport']

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function joursRestants(dateLimite) {
  const diff = Math.ceil((new Date(dateLimite) - new Date()) / (1000 * 60 * 60 * 24))
  return diff
}

function formatMontant(m) {
  if (!m) return '—'
  if (m >= 1_000_000) return `${(m / 1_000_000).toFixed(0)} M FCFA`
  return `${m.toLocaleString('fr-FR')} FCFA`
}

export default function VeilleMarches() {
  const [appels, setAppels] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtreCategorie, setFiltreCategorie] = useState('')
  const [recherche, setRecherche] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    getAppelsOffres(filtreCategorie ? { categorie: filtreCategorie } : {})
      .then((res) => setAppels(res.data))
      .finally(() => setLoading(false))
  }, [filtreCategorie])

  const appelsFiltres = appels.filter(
    (a) =>
      a.statut !== 'archive' &&
      (a.objet.toLowerCase().includes(recherche.toLowerCase()) || a.reference.toLowerCase().includes(recherche.toLowerCase()))
  )

  return (
    <div>
      <PageHeader
        eyebrow="Module Veille Marchés"
        title="Appels d'offres détectés"
        subtitle="Collecte automatique des opportunités publiques et privées en Côte d'Ivoire et auprès des organisations internationales."
      />

      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: '1 1 260px', maxWidth: 360 }}>
          <Search size={16} style={{ position: 'absolute', left: 13, top: 12, color: 'var(--ardoise-clair)' }} />
          <input
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
            placeholder="Rechercher par objet ou référence…"
            style={{
              width: '100%',
              padding: '10px 14px 10px 36px',
              borderRadius: 8,
              border: '1px solid var(--bordure)',
              fontSize: 14,
              background: '#fff',
            }}
          />
        </div>
        <select
          value={filtreCategorie}
          onChange={(e) => setFiltreCategorie(e.target.value)}
          style={{ padding: '10px 14px', borderRadius: 8, border: '1px solid var(--bordure)', fontSize: 14, background: '#fff', color: 'var(--ardoise)' }}
        >
          <option value="">Toutes catégories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <Loader label="Recherche des appels d'offres…" />
      ) : appelsFiltres.length === 0 ? (
        <EmptyState icon={Search} title="Aucun appel d'offres trouvé" description="Essayez d'élargir vos critères de recherche." />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {appelsFiltres.map((ao) => {
            const jours = joursRestants(ao.date_limite)
            const urgent = jours <= 7 && jours >= 0 && !['gagne', 'perdu', 'archive'].includes(ao.statut)
            return (
              <Card
                key={ao.id}
                onClick={() => navigate(`/appels-offres/${ao.id}`)}
                style={{ padding: '18px 22px', cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6, flexWrap: 'wrap' }}>
                      <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--or-accent)', letterSpacing: '0.03em' }}>{ao.reference}</span>
                      <StatusBadge status={ao.statut} />
                      {urgent && <StatusBadge status="en_analyse" />}
                    </div>
                    <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--ardoise)', fontFamily: 'var(--font-body)', marginBottom: 8, lineHeight: 1.35 }}>
                      {ao.objet}
                    </h3>
                    <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', fontSize: 13, color: 'var(--ardoise-clair)' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Building size={14} /> {ao.source}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Calendar size={14} /> Limite : {formatDate(ao.date_limite)}
                        {jours >= 0 && !['gagne', 'perdu'].includes(ao.statut) && (
                          <span style={{ color: urgent ? 'var(--rouge-alerte)' : 'inherit', fontWeight: urgent ? 700 : 400 }}>
                            {' '}(J-{jours})
                          </span>
                        )}
                      </span>
                      <span style={{ fontWeight: 600, color: 'var(--bleu-institutionnel)' }}>{formatMontant(ao.montant_estimatif)}</span>
                    </div>
                  </div>
                  <ChevronRight size={20} color="var(--ardoise-clair)" style={{ flexShrink: 0, marginTop: 4 }} />
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
