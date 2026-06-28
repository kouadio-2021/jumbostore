import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Radar, FileStack, Trophy, Wallet, TrendingUp } from 'lucide-react'
import { getDashboardStats } from '../services/api.js'
import { Card, PageHeader, Loader } from '../components/UI.jsx'

const COULEURS_CATEGORIE = {
  BTP: '#0E3A5C',
  Informatique: '#C9912A',
  Fournitures: '#2D7D5A',
  'Électricité': '#5B3FA0',
  Hydraulique: '#1B8A9E',
  'Sécurité': '#C0392B',
  Transport: '#B8762E',
}

function formatFCFA(valeur) {
  if (valeur >= 1_000_000_000) return `${(valeur / 1_000_000_000).toFixed(1)} Md FCFA`
  if (valeur >= 1_000_000) return `${(valeur / 1_000_000).toFixed(1)} M FCFA`
  return `${Math.round(valeur).toLocaleString('fr-FR')} FCFA`
}

function StatCard({ icon: Icon, label, value, accent }) {
  return (
    <Card style={{ padding: '22px 22px 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: 12.5, color: 'var(--ardoise-clair)', fontWeight: 600, marginBottom: 8 }}>{label}</div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 26, fontWeight: 700, color: 'var(--bleu-institutionnel)' }}>{value}</div>
        </div>
        <div style={{ width: 42, height: 42, borderRadius: 10, background: accent + '18', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon size={20} color={accent} />
        </div>
      </div>
    </Card>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [erreur, setErreur] = useState(null)

  useEffect(() => {
    getDashboardStats()
      .then((res) => setStats(res.data))
      .catch(() => setErreur('Impossible de charger les statistiques. Vérifiez que le serveur backend est démarré.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loader label="Chargement du tableau de bord…" />
  if (erreur) return <Card style={{ padding: 24, color: 'var(--rouge-alerte)' }}>{erreur}</Card>
  if (!stats) return null

  const dataCategories = Object.entries(stats.appels_par_categorie).map(([nom, valeur]) => ({ nom, valeur }))
  const dataStatuts = Object.entries(stats.appels_par_statut).map(([nom, valeur]) => ({ nom, valeur }))

  return (
    <div>
      <PageHeader
        eyebrow="Pilotage"
        title="Tableau de bord"
        subtitle="Vue d'ensemble de l'activité de veille marchés et de soumission aux appels d'offres de Jumbo Store SARL."
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 28 }}>
        <StatCard icon={Radar} label="Appels d'offres détectés" value={stats.nombre_appels_detectes} accent="#0E3A5C" />
        <StatCard icon={FileStack} label="Soumissions en cours" value={stats.nombre_soumissions} accent="#C9912A" />
        <StatCard icon={TrendingUp} label="Taux de conformité" value={`${stats.taux_conformite}%`} accent="#2D7D5A" />
        <StatCard icon={Trophy} label="Marchés gagnés" value={stats.marches_gagnes} accent="#5B3FA0" />
        <StatCard icon={Wallet} label="CA potentiel en cours" value={formatFCFA(stats.chiffre_affaires_potentiel)} accent="#B8762E" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 20 }}>
        <Card style={{ padding: 24 }}>
          <h3 style={{ fontSize: 16, marginBottom: 4 }}>Appels d'offres par catégorie</h3>
          <p style={{ fontSize: 13, color: 'var(--ardoise-clair)', marginBottom: 16 }}>Répartition sectorielle des opportunités détectées</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={dataCategories} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
              <XAxis dataKey="nom" tick={{ fontSize: 11.5, fill: 'var(--ardoise-clair)' }} axisLine={{ stroke: 'var(--bordure)' }} tickLine={false} />
              <YAxis tick={{ fontSize: 11.5, fill: 'var(--ardoise-clair)' }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: '1px solid var(--bordure)', fontSize: 13 }}
                cursor={{ fill: 'rgba(14,58,92,0.04)' }}
              />
              <Bar dataKey="valeur" radius={[6, 6, 0, 0]}>
                {dataCategories.map((entry, i) => (
                  <Cell key={i} fill={COULEURS_CATEGORIE[entry.nom] || '#0E3A5C'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card style={{ padding: 24 }}>
          <h3 style={{ fontSize: 16, marginBottom: 4 }}>Répartition par statut</h3>
          <p style={{ fontSize: 13, color: 'var(--ardoise-clair)', marginBottom: 16 }}>État du portefeuille d'opportunités</p>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={dataStatuts}
                dataKey="valeur"
                nameKey="nom"
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={2}
              >
                {dataStatuts.map((_, i) => (
                  <Cell key={i} fill={['#0E3A5C', '#C9912A', '#2D7D5A', '#5B3FA0', '#C0392B', '#6B7280', '#1B8A9E'][i % 7]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid var(--bordure)', fontSize: 13 }} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 8, justifyContent: 'center' }}>
            {dataStatuts.map((s, i) => (
              <div key={s.nom} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11.5, color: 'var(--ardoise-clair)' }}>
                <span style={{ width: 8, height: 8, borderRadius: 4, background: ['#0E3A5C', '#C9912A', '#2D7D5A', '#5B3FA0', '#C0392B', '#6B7280', '#1B8A9E'][i % 7] }} />
                {s.nom.replace(/_/g, ' ')}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
