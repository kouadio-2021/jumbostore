import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import VeilleMarches from './pages/VeilleMarches.jsx'
import DetailAppelOffres from './pages/DetailAppelOffres.jsx'
import ProfilEntreprise from './pages/ProfilEntreprise.jsx'
import Soumissions from './pages/Soumissions.jsx'
import DetailSoumission from './pages/DetailSoumission.jsx'
import Comparateur from './pages/Comparateur.jsx'
import Facturation from './pages/Facturation.jsx'
import Notifications from './pages/Notifications.jsx'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/tableau-de-bord" replace />} />
        <Route path="/tableau-de-bord" element={<Dashboard />} />
        <Route path="/appels-offres" element={<VeilleMarches />} />
        <Route path="/appels-offres/:id" element={<DetailAppelOffres />} />
        <Route path="/entreprise" element={<ProfilEntreprise />} />
        <Route path="/soumissions" element={<Soumissions />} />
        <Route path="/soumissions/:id" element={<DetailSoumission />} />
        <Route path="/comparateur" element={<Comparateur />} />
        <Route path="/facturation" element={<Facturation />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="*" element={<Navigate to="/tableau-de-bord" replace />} />
      </Routes>
    </Layout>
  )
}
