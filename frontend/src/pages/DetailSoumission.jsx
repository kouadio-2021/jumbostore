import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, FileText, FileSpreadsheet, File, Download, Sparkles, CheckCircle2 } from 'lucide-react'
import { getSoumission, genererDocuments, validerSoumission, telechargerDocumentUrl } from '../services/api.js'
import { Card, Loader, PrimaryButton, SecondaryButton } from '../components/UI.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

const TYPES_DOCUMENTS = [
  { type: 'Offre Technique', icon: FileText, format: 'PDF' },
  { type: 'Offre Financière', icon: FileSpreadsheet, format: 'XLSX' },
  { type: 'Lettre de soumission', icon: File, format: 'DOCX' },
]

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'
}

export default function DetailSoumission() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [soumission, setSoumission] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generation, setGeneration] = useState(false)
  const [validation, setValidation] = useState(false)

  const charger = () => getSoumission(id).then((res) => setSoumission(res.data))

  useEffect(() => {
    setLoading(true)
    charger().finally(() => setLoading(false))
  }, [id])

  const lancerGeneration = async () => {
    setGeneration(true)
    try {
      await genererDocuments(parseInt(id), TYPES_DOCUMENTS.map((d) => d.type))
      await charger()
    } finally {
      setGeneration(false)
    }
  }

  const valider = async () => {
    setValidation(true)
    try {
      await validerSoumission(parseInt(id), 'Karimu Waidi Abiola (PDG)')
      await charger()
    } finally {
      setValidation(false)
    }
  }

  if (loading) return <Loader label="Chargement de la soumission…" />
  if (!soumission) return <Card style={{ padding: 24 }}>Soumission introuvable.</Card>

  const documentsExistants = soumission.documents.reduce((acc, d) => ({ ...acc, [d.type_document]: d }), {})

  return (
    <div>
      <button onClick={() => navigate('/soumissions')} style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--ardoise-clair)', fontSize: 13.5, marginBottom: 18, fontWeight: 500 }}>
        <ArrowLeft size={16} /> Retour aux soumissions
      </button>

      <Card style={{ padding: '26px 28px', marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16, flexWrap: 'wrap' }}>
          <div>
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8 }}>
              <h1 style={{ fontSize: 22 }}>Soumission #{soumission.id}</h1>
              <StatusBadge status={soumission.statut} />
            </div>
            <p style={{ color: 'var(--ardoise-clair)', fontSize: 14 }}>Créée le {formatDate(soumission.date_creation)}</p>
            {soumission.date_validation && (
              <p style={{ color: 'var(--vert-validation)', fontSize: 13.5, marginTop: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
                <CheckCircle2 size={15} /> Validée par {soumission.valide_par} le {formatDate(soumission.date_validation)}
              </p>
            )}
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            {soumission.documents.length === 0 ? (
              <PrimaryButton onClick={lancerGeneration} disabled={generation}>
                <Sparkles size={16} /> {generation ? 'Génération en cours…' : 'Générer les documents'}
              </PrimaryButton>
            ) : soumission.statut !== 'validee' ? (
              <PrimaryButton onClick={valider} disabled={validation} style={{ background: 'var(--vert-validation)' }}>
                <CheckCircle2 size={16} /> {validation ? 'Validation…' : 'Valider la soumission'}
              </PrimaryButton>
            ) : null}
          </div>
        </div>
      </Card>

      <h3 style={{ fontSize: 16, marginBottom: 14 }}>Documents de soumission</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14 }}>
        {TYPES_DOCUMENTS.map(({ type, icon: Icon, format }) => {
          const doc = documentsExistants[type]
          return (
            <Card key={type} style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
                <div style={{ width: 38, height: 38, borderRadius: 9, background: '#E2EEF9', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon size={18} color="var(--bleu-institutionnel)" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{type}</div>
                  <div style={{ fontSize: 12, color: 'var(--ardoise-clair)' }}>Format {format}</div>
                </div>
              </div>
              {doc ? (
                <a href={telechargerDocumentUrl(doc.id)} target="_blank" rel="noreferrer">
                  <SecondaryButton style={{ width: '100%', justifyContent: 'center' }}>
                    <Download size={15} /> Télécharger
                  </SecondaryButton>
                </a>
              ) : (
                <div style={{ fontSize: 12.5, color: 'var(--ardoise-clair)', fontStyle: 'italic' }}>Pas encore généré</div>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
