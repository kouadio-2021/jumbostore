import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jumbostore_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// --- Auth ---
export const login = (email, password) => api.post('/api/auth/login', { email, password })
export const getMe = () => api.get('/api/auth/me')

// --- Dashboard ---
export const getDashboardStats = () => api.get('/api/dashboard/stats')

// --- Appels d'offres ---
export const getAppelsOffres = (params) => api.get('/api/appels-offres', { params })
export const getAppelOffres = (id) => api.get(`/api/appels-offres/${id}`)
export const createAppelOffres = (data) => api.post('/api/appels-offres', data)
export const updateStatutAppelOffres = (id, statut) => api.patch(`/api/appels-offres/${id}/statut`, { statut })
export const archiverAppelOffres = (id) => api.delete(`/api/appels-offres/${id}`)

// --- Entreprises (plusieurs profils possibles) ---
export const getEntreprises = () => api.get('/api/entreprises')
export const getEntreprise = (id) => api.get(`/api/entreprises/${id}`)
export const createEntreprise = (data) => api.post('/api/entreprises', data)
export const updateEntreprise = (id, data) => api.patch(`/api/entreprises/${id}`, data)
export const deleteEntreprise = (id) => api.delete(`/api/entreprises/${id}`)
export const uploadDocumentEntreprise = (entrepriseId, formData) =>
  api.post(`/api/entreprises/${entrepriseId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const deleteDocumentEntreprise = (documentId) => api.delete(`/api/entreprises/documents/${documentId}`)

// --- Analyse DAO ---
export const lancerAnalyseDAO = (appel_offres_id) => api.post('/api/analyse-dao', { appel_offres_id })
export const getAnalyseDAO = (aoId) => api.get(`/api/analyse-dao/${aoId}`)

// --- Soumissions ---
export const getSoumissions = () => api.get('/api/soumissions')
export const getSoumission = (id) => api.get(`/api/soumissions/${id}`)
export const createSoumission = (data) => api.post('/api/soumissions', data)
export const genererDocuments = (soumission_id, types_documents) =>
  api.post('/api/soumissions/generer-documents', { soumission_id, types_documents })
export const validerSoumission = (id, valide_par) =>
  api.patch(`/api/soumissions/${id}/valider`, null, { params: { valide_par } })
export const telechargerDocumentUrl = (documentId) => `${API_URL}/api/soumissions/documents/${documentId}/telecharger`

// --- Comparateur ---
export const rechercherPrix = (designation, quantite) => api.post('/api/comparateur/rechercher', { designation, quantite })
export const getHistoriqueComparateur = () => api.get('/api/comparateur/historique')

// --- Factures ---
export const getFactures = () => api.get('/api/factures')
export const getFacture = (id) => api.get(`/api/factures/${id}`)
export const createFacture = (data) => api.post('/api/factures', data)
export const updateStatutFacture = (id, statut) => api.patch(`/api/factures/${id}/statut`, null, { params: { statut } })

// --- Notifications ---
export const getNotifications = (nonLuesSeulement = false) =>
  api.get('/api/notifications', { params: { non_lues_seulement: nonLuesSeulement } })
export const marquerNotificationLue = (id) => api.patch(`/api/notifications/${id}/lire`)
export const marquerToutesLues = () => api.patch('/api/notifications/lire-tout')

export default api
