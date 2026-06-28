import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Sparkles, AlertTriangle, FileCheck2, Building, Calendar, Coins, Clock } from 'lucide-react'
import { getAppelOffres, lancerAnalyseDAO, getAnalyseDAO, createSoumission } from '../services/api.js'
import { Card, Loader, PrimaryButton, SecondaryButton } from '../components/UI.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import ScoreGauge from '../components/ScoreGauge.jsx'

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
}
function formatMontant(m, devise = 'FCFA') {
  if (!m) return '—'
  return `${m.toLocaleString('fr-FR')} ${devise}`
}

export default function DetailAppelOffres() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [ao, setAo] = useState(null)
  const [analyse, setAnalyse] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyseEnCours, setAnalyseEnCours] = useState(false)
  const [creationEnCours, setCreationEnCours] = useState(false)

  useEffect(() => {
    setLoading(true)
    getAppelOffres(id)
      .then((res) => setAo(res.data))
      .then(() =>
        getAnalyseDAO(id)
          .then((res) => setAnalyse(res.data))
          .catch(() => setAnalyse(null))
      )
      .finally(() => setLoading(false))
  }, [id])

  const lancerAnalyse = async () => {
    setAnalyseEnCours(true)
    try {
      const res = await lancerAnalyseDAO(parseInt(id))
      setAnalyse(res.data)
      setAo((prev) => ({ ...prev, score_compatibilite: res.data.score_compatibilite, statut: prev.statut === 'nouveau' ? 'en_analyse' : prev.statut }))
    } finally {
      setAnalyseEnCours(false)
    }
  }

  const demarrerSoumission = async () => {
    setCreationEnCours(true)
    try {
      const res = await createSoumission({ appel_offres_id: parseInt(id) })
      navigate(`/soumissions/${res.data.id}`)
    } finally {
      setCreationEnCours(false)
    }
  }

  if (loading) return <Loader label="Chargement de l'appel d'offres…" />
  if (!ao) return <Card style={{ padding: 24 }}>Appel d'offres introuvable.</Card>

  const pointsAttention = analyse?.points_attention ? JSON.parse(analyse.points_attention) : []
  const documentsRequis = analyse?.documents_requis ? JSON.parse(analyse.documents_requis) : []
  const delais = analyse?.delais ? JSON.parse(analyse.delais) : null
  const criteresFinanciers = analyse?.criteres_financiers ? JSON.parse(analyse.criteres_financiers) : null
  const conditionsAdmin = analyse?.conditions_administratives ? JSON.parse(analyse.conditions_administratives) : null

  return (
    <div>
      <button onClick={() => navigate('/appels-offres')} style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--ardoise-clair)', fontSize: 13.5, marginBottom: 18, fontWeight: 500 }}>
        <ArrowLeft size={16} /> Retour à la veille marchés
      </button>

      <Card style={{ padding: '26px 28px', marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 20, flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8, flexWrap: 'wrap' }}>
              <span style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--or-accent)', letterSpacing: '0.03em' }}>{ao.reference}</span>
              <StatusBadge status={ao.statut} />
            </div>
            <h1 style={{ fontSize: 22, lineHeight: 1.35, marginBottom: 16 }}>{ao.objet}</h1>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 14, color: 'var(--ardoise)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Building size={15} color="var(--ardoise-clair)" /> {ao.source} — {ao.type_avis}</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Calendar size={15} color="var(--ardoise-clair)" /> Publié le {formatDate(ao.date_publication)} · Limite : {formatDate(ao.date_limite)}</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Coins size={15} color="var(--ardoise-clair)" /> Montant estimatif : {formatMontant(ao.montant_estimatif, ao.devise)}</span>
            </div>
          </div>

          {ao.score_compatibilite != null && <ScoreGauge score={ao.score_compatibilite} label="Score de compatibilité" />}
        </div>

        <div style={{ display: 'flex', gap: 12, marginTop: 22, flexWrap: 'wrap' }}>
          {!analyse ? (
            <PrimaryButton onClick={lancerAnalyse} disabled={analyseEnCours}>
              <Sparkles size={16} /> {analyseEnCours ? 'Analyse en cours…' : 'Lancer l\'analyse IA du DAO'}
            </PrimaryButton>
          ) : (
            <SecondaryButton onClick={lancerAnalyse} disabled={analyseEnCours}>
              <Sparkles size={16} /> Relancer l'analyse
            </SecondaryButton>
          )}
          {analyse && (
            <PrimaryButton onClick={demarrerSoumission} disabled={creationEnCours} style={{ background: 'var(--or-accent)' }}>
              <FileCheck2 size={16} /> {creationEnCours ? 'Création…' : 'Démarrer la soumission'}
            </PrimaryButton>
          )}
        </div>
      </Card>

      {analyse && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <Card style={{ padding: 22 }}>
            <h3 style={{ fontSize: 15.5, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <AlertTriangle size={17} color="var(--ambre-attention)" /> Points d'attention
            </h3>
            <ul style={{ margin: 0, paddingLeft: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10 }}>
              {pointsAttention.map((p, i) => (
                <li key={i} style={{ display: 'flex', gap: 10, fontSize: 13.5, color: 'var(--ardoise)', lineHeight: 1.5 }}>
                  <span style={{ width: 5, height: 5, borderRadius: 3, background: 'var(--ambre-attention)', marginTop: 7, flexShrink: 0 }} />
                  {p}
                </li>
              ))}
            </ul>
          </Card>

          <Card style={{ padding: 22 }}>
            <h3 style={{ fontSize: 15.5, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <FileCheck2 size={17} color="var(--vert-validation)" /> Documents requis
            </h3>
            <ul style={{ margin: 0, paddingLeft: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 9 }}>
              {documentsRequis.map((d, i) => (
                <li key={i} style={{ display: 'flex', gap: 10, fontSize: 13.5, color: 'var(--ardoise)' }}>
                  <span style={{ width: 5, height: 5, borderRadius: 3, background: 'var(--vert-validation)', marginTop: 7, flexShrink: 0 }} />
                  {d}
                </li>
              ))}
            </ul>
          </Card>

          {delais && (
            <Card style={{ padding: 22 }}>
              <h3 style={{ fontSize: 15.5, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Clock size={17} color="var(--bleu-institutionnel)" /> Délais
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13.5 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--ardoise-clair)' }}>Délai de remise de l'offre</span><strong>{delais.delai_remise_offre_jours} jours</strong></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--ardoise-clair)' }}>Délai d'exécution du marché</span><strong>{delais.delai_execution_marche_mois} mois</strong></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--ardoise-clair)' }}>Validité de l'offre</span><strong>{delais.validite_offre_jours} jours</strong></div>
              </div>
            </Card>
          )}

          {conditionsAdmin && criteresFinanciers && (
            <Card style={{ padding: 22 }}>
              <h3 style={{ fontSize: 15.5, marginBottom: 14 }}>Conditions clés</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13.5 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--ardoise-clair)' }}>Caution provisoire</span><strong>{conditionsAdmin.taux_caution_provisoire}</strong></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--ardoise-clair)' }}>Agrément requis</span><strong>{conditionsAdmin.agrement_requis ? 'Oui' : 'Non'}</strong></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--ardoise-clair)' }}>Ancienneté RCCM min.</span><strong>{conditionsAdmin.registre_commerce_anciennete_min_annees} ans</strong></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--ardoise-clair)' }}>Garantie financière exigée</span><strong>{criteresFinanciers.garantie_financiere_exigee ? 'Oui' : 'Non'}</strong></div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
