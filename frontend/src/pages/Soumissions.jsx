import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileStack, ChevronRight } from 'lucide-react'
import { getSoumissions } from '../services/api.js'
import { Card, PageHeader, Loader, EmptyState } from '../components/UI.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

function formatDate(d) {
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

export default function Soumissions() {
  const [soumissions, setSoumissions] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getSoumissions().then((res) => setSoumissions(res.data)).finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <PageHeader
        eyebrow="Module Génération Automatique"
        title="Soumissions"
        subtitle="Suivi des dossiers de soumission et génération des documents techniques, financiers et administratifs."
      />

      {loading ? (
        <Loader label="Chargement des soumissions…" />
      ) : soumissions.length === 0 ? (
        <EmptyState
          icon={FileStack}
          title="Aucune soumission en cours"
          description="Lancez l'analyse d'un appel d'offres puis cliquez sur « Démarrer la soumission » pour en créer une."
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {soumissions.map((s) => (
            <Card key={s.id} onClick={() => navigate(`/soumissions/${s.id}`)} style={{ padding: '18px 22px', cursor: 'pointer' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 6 }}>
                    <span style={{ fontWeight: 600, fontSize: 15 }}>Soumission #{s.id}</span>
                    <StatusBadge status={s.statut} />
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--ardoise-clair)' }}>
                    Créée le {formatDate(s.date_creation)} · {s.documents.length} document(s) généré(s)
                  </div>
                </div>
                <ChevronRight size={20} color="var(--ardoise-clair)" />
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
