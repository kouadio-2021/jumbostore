import React, { useEffect, useState } from 'react'
import { Plus, Receipt, Trash2, X } from 'lucide-react'
import { getFactures, createFacture } from '../services/api.js'
import { Card, PageHeader, Loader, EmptyState, PrimaryButton, SecondaryButton } from '../components/UI.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

const TYPES = ['Proforma', 'Facture', 'Devis', 'Bon de commande']

function formatFCFA(v) {
  return `${Math.round(v).toLocaleString('fr-FR')} FCFA`
}
function formatDate(d) {
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function ModaleNouveauDocument({ onClose, onCree }) {
  const [typeDocument, setTypeDocument] = useState('Proforma')
  const [clientNom, setClientNom] = useState('')
  const [clientAdresse, setClientAdresse] = useState('')
  const [lignes, setLignes] = useState([{ designation: '', quantite: 1, prix_unitaire: 0 }])
  const [envoi, setEnvoi] = useState(false)

  const ajouterLigne = () => setLignes([...lignes, { designation: '', quantite: 1, prix_unitaire: 0 }])
  const supprimerLigne = (i) => setLignes(lignes.filter((_, idx) => idx !== i))
  const majLigne = (i, champ, valeur) => {
    const copie = [...lignes]
    copie[i][champ] = valeur
    setLignes(copie)
  }

  const totalHT = lignes.reduce((acc, l) => acc + (parseFloat(l.quantite) || 0) * (parseFloat(l.prix_unitaire) || 0), 0)

  const soumettre = async (e) => {
    e.preventDefault()
    if (!clientNom.trim() || lignes.some((l) => !l.designation.trim())) return
    setEnvoi(true)
    try {
      await createFacture({
        type_document: typeDocument,
        client_nom: clientNom,
        client_adresse: clientAdresse,
        tva_taux: 18.0,
        lignes: lignes.map((l) => ({ ...l, quantite: parseFloat(l.quantite), prix_unitaire: parseFloat(l.prix_unitaire) })),
      })
      onCree()
      onClose()
    } finally {
      setEnvoi(false)
    }
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(8,42,68,0.45)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20, zIndex: 100 }}>
      <Card style={{ padding: 28, width: '100%', maxWidth: 560, maxHeight: '88vh', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 style={{ fontSize: 18 }}>Nouveau document</h3>
          <button onClick={onClose} style={{ color: 'var(--ardoise-clair)' }}><X size={20} /></button>
        </div>
        <form onSubmit={soumettre} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <select value={typeDocument} onChange={(e) => setTypeDocument(e.target.value)} style={{ padding: 11, borderRadius: 8, border: '1px solid var(--bordure)', fontSize: 14 }}>
            {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <input placeholder="Nom du client" value={clientNom} onChange={(e) => setClientNom(e.target.value)} required style={{ padding: 11, borderRadius: 8, border: '1px solid var(--bordure)', fontSize: 14 }} />
          <input placeholder="Adresse du client (optionnel)" value={clientAdresse} onChange={(e) => setClientAdresse(e.target.value)} style={{ padding: 11, borderRadius: 8, border: '1px solid var(--bordure)', fontSize: 14 }} />

          <div style={{ fontSize: 13, fontWeight: 600, marginTop: 4 }}>Lignes</div>
          {lignes.map((l, i) => (
            <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input placeholder="Désignation" value={l.designation} onChange={(e) => majLigne(i, 'designation', e.target.value)} required style={{ flex: 2, padding: 9, borderRadius: 7, border: '1px solid var(--bordure)', fontSize: 13.5 }} />
              <input type="number" min={0} placeholder="Qté" value={l.quantite} onChange={(e) => majLigne(i, 'quantite', e.target.value)} style={{ width: 64, padding: 9, borderRadius: 7, border: '1px solid var(--bordure)', fontSize: 13.5 }} />
              <input type="number" min={0} placeholder="Prix unit." value={l.prix_unitaire} onChange={(e) => majLigne(i, 'prix_unitaire', e.target.value)} style={{ width: 110, padding: 9, borderRadius: 7, border: '1px solid var(--bordure)', fontSize: 13.5 }} />
              {lignes.length > 1 && (
                <button type="button" onClick={() => supprimerLigne(i)} style={{ color: 'var(--rouge-alerte)' }}><Trash2 size={16} /></button>
              )}
            </div>
          ))}
          <button type="button" onClick={ajouterLigne} style={{ fontSize: 13, color: 'var(--bleu-institutionnel)', fontWeight: 600, textAlign: 'left' }}>+ Ajouter une ligne</button>

          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderTop: '1px solid var(--bordure)', marginTop: 6 }}>
            <span style={{ fontWeight: 600 }}>Total HT</span>
            <span style={{ fontWeight: 700, color: 'var(--bleu-institutionnel)' }}>{formatFCFA(totalHT)}</span>
          </div>

          <PrimaryButton type="submit" disabled={envoi} style={{ justifyContent: 'center', marginTop: 4 }}>
            {envoi ? 'Création…' : 'Créer le document'}
          </PrimaryButton>
        </form>
      </Card>
    </div>
  )
}

export default function Facturation() {
  const [factures, setFactures] = useState([])
  const [loading, setLoading] = useState(true)
  const [modaleOuverte, setModaleOuverte] = useState(false)

  const charger = () => getFactures().then((res) => setFactures(res.data))

  useEffect(() => {
    charger().finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <PageHeader
        eyebrow="Module Facturation"
        title="Proformas, factures &amp; devis"
        subtitle="Génération des documents commerciaux de Jumbo Store SARL."
        action={
          <PrimaryButton onClick={() => setModaleOuverte(true)}>
            <Plus size={16} /> Nouveau document
          </PrimaryButton>
        }
      />

      {loading ? (
        <Loader label="Chargement des documents…" />
      ) : factures.length === 0 ? (
        <EmptyState icon={Receipt} title="Aucun document pour le moment" description="Créez votre premier proforma, devis ou facture." />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {factures.map((f) => (
            <Card key={f.id} style={{ padding: '18px 22px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                <div>
                  <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 4 }}>
                    <span style={{ fontWeight: 700, fontSize: 14 }}>{f.numero}</span>
                    <StatusBadge status={f.statut} />
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--ardoise-clair)' }}>{f.type_document} · {f.client_nom} · {formatDate(f.date_emission)}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 11.5, color: 'var(--ardoise-clair)' }}>Montant TTC</div>
                  <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--bleu-institutionnel)' }}>{formatFCFA(f.montant_ttc)}</div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {modaleOuverte && <ModaleNouveauDocument onClose={() => setModaleOuverte(false)} onCree={charger} />}
    </div>
  )
}
