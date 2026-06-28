import React, { useEffect, useState } from 'react'
import { Building2, FileCheck, AlertCircle, Award, Briefcase, Plus, Upload } from 'lucide-react'
import { getEntreprises, createEntreprise, uploadDocumentEntreprise } from '../services/api.js'
import { Card, PageHeader, Loader } from '../components/UI.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

function formatFCFA(v) {
  return `${((v || 0) / 1_000_000).toFixed(0)} M FCFA`
}
function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'
}

function FormulaireNouvelleEntreprise({ onCreated, onCancel }) {
  const [form, setForm] = useState({ raison_sociale: '', rccm: '', dfe: '', cnps: '', attestation_fiscale: '', adresse: '' })
  const [enCours, setEnCours] = useState(false)

  const soumettre = async (e) => {
    e.preventDefault()
    if (!form.raison_sociale.trim()) return
    setEnCours(true)
    try {
      const res = await createEntreprise({ ...form, domaines_expertise: [], secteurs: [] })
      onCreated(res.data)
    } finally {
      setEnCours(false)
    }
  }

  return (
    <Card style={{ padding: 22, marginBottom: 24 }}>
      <h3 style={{ fontSize: 16, marginBottom: 16 }}>Nouvelle entreprise</h3>
      <form onSubmit={soumettre} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <input placeholder="Raison sociale *" value={form.raison_sociale}
          onChange={(e) => setForm({ ...form, raison_sociale: e.target.value })}
          style={{ padding: 10, borderRadius: 8, border: '1px solid var(--bordure)', gridColumn: '1 / -1' }} required />
        <input placeholder="RCCM" value={form.rccm} onChange={(e) => setForm({ ...form, rccm: e.target.value })}
          style={{ padding: 10, borderRadius: 8, border: '1px solid var(--bordure)' }} />
        <input placeholder="DFE" value={form.dfe} onChange={(e) => setForm({ ...form, dfe: e.target.value })}
          style={{ padding: 10, borderRadius: 8, border: '1px solid var(--bordure)' }} />
        <input placeholder="CNPS" value={form.cnps} onChange={(e) => setForm({ ...form, cnps: e.target.value })}
          style={{ padding: 10, borderRadius: 8, border: '1px solid var(--bordure)' }} />
        <input placeholder="Attestation fiscale" value={form.attestation_fiscale}
          onChange={(e) => setForm({ ...form, attestation_fiscale: e.target.value })}
          style={{ padding: 10, borderRadius: 8, border: '1px solid var(--bordure)' }} />
        <input placeholder="Adresse" value={form.adresse} onChange={(e) => setForm({ ...form, adresse: e.target.value })}
          style={{ padding: 10, borderRadius: 8, border: '1px solid var(--bordure)', gridColumn: '1 / -1' }} />
        <div style={{ display: 'flex', gap: 10, gridColumn: '1 / -1' }}>
          <button type="submit" disabled={enCours}
            style={{ padding: '10px 18px', borderRadius: 8, background: 'var(--bleu-institutionnel)', color: 'white', border: 'none', fontWeight: 600, cursor: 'pointer' }}>
            {enCours ? 'Création…' : 'Créer l’entreprise'}
          </button>
          <button type="button" onClick={onCancel}
            style={{ padding: '10px 18px', borderRadius: 8, background: 'transparent', border: '1px solid var(--bordure)', cursor: 'pointer' }}>
            Annuler
          </button>
        </div>
      </form>
    </Card>
  )
}

function FormulaireUploadDocument({ entrepriseId, onUploaded }) {
  const [type, setType] = useState('RCCM')
  const [fichier, setFichier] = useState(null)
  const [enCours, setEnCours] = useState(false)

  const envoyer = async () => {
    if (!fichier) return
    setEnCours(true)
    const formData = new FormData()
    formData.append('type_document', type)
    formData.append('fichier', fichier)
    try {
      await uploadDocumentEntreprise(entrepriseId, formData)
      setFichier(null)
      onUploaded()
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 14, flexWrap: 'wrap' }}>
      <select value={type} onChange={(e) => setType(e.target.value)}
        style={{ padding: 8, borderRadius: 8, border: '1px solid var(--bordure)' }}>
        <option>RCCM</option>
        <option>DFE</option>
        <option>CNPS</option>
        <option>Attestation fiscale</option>
        <option>Agrément BTP</option>
      </select>
      <input type="file" onChange={(e) => setFichier(e.target.files[0])} style={{ fontSize: 13 }} />
      <button onClick={envoyer} disabled={!fichier || enCours}
        style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderRadius: 8, background: 'var(--or-accent)', color: 'white', border: 'none', fontWeight: 600, cursor: 'pointer' }}>
        <Upload size={14} /> {enCours ? 'Envoi…' : 'Ajouter le document'}
      </button>
    </div>
  )
}

export default function ProfilEntreprise() {
  const [entreprises, setEntreprises] = useState([])
  const [selectionId, setSelectionId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [afficherFormulaire, setAfficherFormulaire] = useState(false)

  const charger = () => {
    getEntreprises().then((res) => {
      setEntreprises(res.data)
      if (res.data.length > 0 && !selectionId) setSelectionId(res.data[0].id)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { charger() }, [])

  if (loading) return <Loader label="Chargement des entreprises…" />

  const profil = entreprises.find((e) => e.id === selectionId)
  const domaines = profil?.domaines_expertise ? JSON.parse(profil.domaines_expertise) : []

  return (
    <div>
      <PageHeader
        eyebrow="Module Profil Entreprise"
        title="Mes entreprises"
        subtitle="Gérez les entreprises pour lesquelles vous soumissionnez, avec leurs documents légaux et références techniques réels."
      />

      <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
        {entreprises.map((e) => (
          <button key={e.id} onClick={() => setSelectionId(e.id)}
            style={{
              padding: '8px 16px', borderRadius: 20, cursor: 'pointer', fontWeight: 600, fontSize: 13.5,
              border: e.id === selectionId ? '2px solid var(--bleu-institutionnel)' : '1px solid var(--bordure)',
              background: e.id === selectionId ? '#E2EEF9' : 'white',
              color: e.id === selectionId ? 'var(--bleu-institutionnel)' : 'var(--ardoise)',
            }}>
            {e.raison_sociale}
          </button>
        ))}
        <button onClick={() => setAfficherFormulaire(!afficherFormulaire)}
          style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 20, background: 'var(--or-accent)', color: 'white', border: 'none', fontWeight: 600, fontSize: 13.5, cursor: 'pointer' }}>
          <Plus size={15} /> Ajouter une entreprise
        </button>
      </div>

      {afficherFormulaire && (
        <FormulaireNouvelleEntreprise
          onCreated={(nouvelle) => { setAfficherFormulaire(false); charger(); setSelectionId(nouvelle.id) }}
          onCancel={() => setAfficherFormulaire(false)}
        />
      )}

      {!profil && !afficherFormulaire && (
        <Card style={{ padding: 24 }}>Aucune entreprise enregistrée. Cliquez sur « Ajouter une entreprise » pour commencer.</Card>
      )}

      {profil && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16, marginBottom: 24 }}>
            <Card style={{ padding: 22 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <Briefcase size={18} color="var(--bleu-institutionnel)" />
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ardoise-clair)' }}>Capacité financière estimée</span>
              </div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 24, fontWeight: 700, color: 'var(--bleu-institutionnel)' }}>
                {formatFCFA(profil.capacite_financiere)}
              </div>
            </Card>
            <Card style={{ padding: 22 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <Award size={18} color="var(--or-accent)" />
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ardoise-clair)' }}>Score de capacité technique</span>
              </div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 24, fontWeight: 700, color: 'var(--bleu-institutionnel)' }}>
                {profil.capacite_technique_score} / 100
              </div>
            </Card>
            <Card style={{ padding: 22 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <Building2 size={18} color="var(--vert-validation)" />
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ardoise-clair)' }}>Adresse du siège</span>
              </div>
              <div style={{ fontSize: 14.5, color: 'var(--ardoise)', fontWeight: 500 }}>{profil.adresse || 'Non renseignée'}</div>
            </Card>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 24 }}>
            {domaines.map((d) => (
              <span key={d} style={{ padding: '6px 14px', borderRadius: 20, background: '#E2EEF9', color: 'var(--bleu-institutionnel)', fontSize: 13, fontWeight: 600 }}>
                {d}
              </span>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            <Card style={{ padding: 22 }}>
              <h3 style={{ fontSize: 16, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <FileCheck size={18} color="var(--bleu-institutionnel)" /> Documents légaux
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {profil.documents.length === 0 && (
                  <div style={{ fontSize: 13.5, color: 'var(--ardoise-clair)' }}>Aucun document ajouté pour le moment.</div>
                )}
                {profil.documents.map((doc) => (
                  <div key={doc.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 12, borderBottom: '1px solid var(--bordure)' }}>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--ardoise)' }}>{doc.type_document}</div>
                      <div style={{ fontSize: 12, color: 'var(--ardoise-clair)', marginTop: 2 }}>
                        {doc.date_expiration ? `Expire le ${formatDate(doc.date_expiration)}` : 'Sans expiration'}
                      </div>
                    </div>
                    <StatusBadge status={doc.statut} />
                  </div>
                ))}
              </div>
              {profil.documents.some((d) => d.statut === 'expire') && (
                <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginTop: 14, padding: 12, background: 'var(--rouge-alerte-fond)', borderRadius: 8, fontSize: 13, color: 'var(--rouge-alerte)' }}>
                  <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
                  Au moins un document est expiré. Pensez à le renouveler avant votre prochaine soumission pour éviter un rejet administratif.
                </div>
              )}
              <FormulaireUploadDocument entrepriseId={profil.id} onUploaded={charger} />
            </Card>

            <Card style={{ padding: 22 }}>
              <h3 style={{ fontSize: 16, marginBottom: 16 }}>Références techniques</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {profil.references_techniques.length === 0 && (
                  <div style={{ fontSize: 13.5, color: 'var(--ardoise-clair)' }}>Aucune référence technique ajoutée pour le moment.</div>
                )}
                {profil.references_techniques.map((ref) => (
                  <div key={ref.id} style={{ paddingBottom: 12, borderBottom: '1px solid var(--bordure)' }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--ardoise)' }}>{ref.intitule_projet}</div>
                    <div style={{ fontSize: 12.5, color: 'var(--ardoise-clair)', marginTop: 3 }}>
                      {ref.client} · {ref.annee} · {ref.secteur}
                    </div>
                    {ref.montant && (
                      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--or-accent)', marginTop: 4 }}>{formatFCFA(ref.montant)}</div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
