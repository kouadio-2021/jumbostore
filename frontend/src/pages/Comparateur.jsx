import React, { useState } from 'react'
import { Scale, Search, Trophy } from 'lucide-react'
import { rechercherPrix } from '../services/api.js'
import { Card, PageHeader, Loader, PrimaryButton, EmptyState } from '../components/UI.jsx'

const LABELS_TYPE = {
  local: 'Fournisseur local',
  international: 'Fournisseur international',
  distributeur_agree: 'Distributeur agréé',
}

function formatFCFA(v) {
  return `${Math.round(v).toLocaleString('fr-FR')} FCFA`
}

export default function Comparateur() {
  const [designation, setDesignation] = useState('')
  const [quantite, setQuantite] = useState(1)
  const [resultat, setResultat] = useState(null)
  const [loading, setLoading] = useState(false)

  const lancerRecherche = async (e) => {
    e.preventDefault()
    if (!designation.trim()) return
    setLoading(true)
    try {
      const res = await rechercherPrix(designation, quantite)
      setResultat(res.data)
    } finally {
      setLoading(false)
    }
  }

  const offresTriees = resultat ? [...resultat.offres].sort((a, b) => b.note_avantage - a.note_avantage) : []

  return (
    <div>
      <PageHeader
        eyebrow="Module Comparateur de Prix"
        title="Comparateur de prix fournisseurs"
        subtitle="Recherchez un produit pour comparer instantanément les offres locales, internationales et des distributeurs agréés."
      />

      <Card style={{ padding: 24, marginBottom: 24 }}>
        <form onSubmit={lancerRecherche} style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: '2 1 320px' }}>
            <Search size={16} style={{ position: 'absolute', left: 13, top: 13, color: 'var(--ardoise-clair)' }} />
            <input
              value={designation}
              onChange={(e) => setDesignation(e.target.value)}
              placeholder="Ex : 50 ordinateurs portables Dell"
              style={{ width: '100%', padding: '11px 14px 11px 36px', borderRadius: 8, border: '1px solid var(--bordure)', fontSize: 14.5 }}
            />
          </div>
          <input
            type="number"
            min={1}
            value={quantite}
            onChange={(e) => setQuantite(parseInt(e.target.value) || 1)}
            style={{ width: 110, padding: '11px 14px', borderRadius: 8, border: '1px solid var(--bordure)', fontSize: 14.5 }}
          />
          <PrimaryButton type="submit" disabled={loading}>
            <Scale size={16} /> {loading ? 'Recherche…' : 'Comparer'}
          </PrimaryButton>
        </form>
        <p style={{ fontSize: 12.5, color: 'var(--ardoise-clair)', marginTop: 10 }}>
          Astuce : indiquez la quantité au début (ex. « 50 ordinateurs portables Dell ») — elle sera détectée automatiquement.
        </p>
      </Card>

      {loading && <Loader label="Recherche des meilleures offres fournisseurs…" />}

      {!loading && resultat && (
        <>
          <h3 style={{ fontSize: 16, marginBottom: 14 }}>
            Résultats pour « {resultat.designation} » — {resultat.quantite} unité(s)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {offresTriees.map((offre, i) => (
              <Card key={offre.id} style={{ padding: '18px 22px', border: i === 0 ? '1.5px solid var(--vert-validation)' : undefined }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 14 }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      {i === 0 && <Trophy size={16} color="var(--or-accent)" />}
                      <span style={{ fontWeight: 700, fontSize: 15 }}>{offre.nom_fournisseur}</span>
                    </div>
                    <div style={{ fontSize: 12.5, color: 'var(--ardoise-clair)' }}>{LABELS_TYPE[offre.type_fournisseur]}</div>
                  </div>
                  <div style={{ display: 'flex', gap: 28, flexWrap: 'wrap' }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 11.5, color: 'var(--ardoise-clair)' }}>Prix unitaire</div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{formatFCFA(offre.prix_unitaire)}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 11.5, color: 'var(--ardoise-clair)' }}>Prix total</div>
                      <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--bleu-institutionnel)' }}>{formatFCFA(offre.prix_total)}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 11.5, color: 'var(--ardoise-clair)' }}>Délai</div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{offre.delai_livraison_jours} j</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 11.5, color: 'var(--ardoise-clair)' }}>Garantie</div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{offre.garantie_mois} mois</div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </>
      )}

      {!loading && !resultat && (
        <EmptyState icon={Scale} title="Lancez votre première comparaison" description="Saisissez un produit ci-dessus pour voir les offres fournisseurs classées par avantage." />
      )}
    </div>
  )
}
