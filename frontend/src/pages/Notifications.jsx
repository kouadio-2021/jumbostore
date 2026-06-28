import React, { useEffect, useState } from 'react'
import { Bell, MessageCircle, Mail, Smartphone, Send, CheckCheck } from 'lucide-react'
import { getNotifications, marquerNotificationLue, marquerToutesLues } from '../services/api.js'
import { Card, PageHeader, Loader, EmptyState, SecondaryButton } from '../components/UI.jsx'

const ICONES_CANAL = {
  WhatsApp: MessageCircle,
  Email: Mail,
  SMS: Smartphone,
  Telegram: Send,
  'Système': Bell,
}

function tempsRelatif(dateStr) {
  const diffMs = new Date() - new Date(dateStr)
  const heures = Math.floor(diffMs / (1000 * 60 * 60))
  if (heures < 1) return "À l'instant"
  if (heures < 24) return `Il y a ${heures} h`
  const jours = Math.floor(heures / 24)
  return `Il y a ${jours} j`
}

export default function Notifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  const charger = () => getNotifications().then((res) => setNotifications(res.data))

  useEffect(() => {
    charger().finally(() => setLoading(false))
  }, [])

  const marquerLue = async (id) => {
    await marquerNotificationLue(id)
    charger()
  }

  const marquerTout = async () => {
    await marquerToutesLues()
    charger()
  }

  const nonLues = notifications.filter((n) => !n.lue).length

  return (
    <div>
      <PageHeader
        eyebrow="Module Notifications"
        title="Notifications"
        subtitle="Alertes multi-canal : nouveaux appels d'offres, échéances proches, pièces manquantes et validations."
        action={nonLues > 0 && <SecondaryButton onClick={marquerTout}><CheckCheck size={15} /> Tout marquer comme lu</SecondaryButton>}
      />

      {loading ? (
        <Loader label="Chargement des notifications…" />
      ) : notifications.length === 0 ? (
        <EmptyState icon={Bell} title="Aucune notification" description="Vous serez alerté ici des nouvelles opportunités et échéances importantes." />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {notifications.map((n) => {
            const Icon = ICONES_CANAL[n.canal] || Bell
            return (
              <Card
                key={n.id}
                onClick={() => !n.lue && marquerLue(n.id)}
                style={{
                  padding: '16px 20px',
                  cursor: n.lue ? 'default' : 'pointer',
                  background: n.lue ? 'var(--fond-blanc)' : '#F7FAFD',
                  borderLeft: n.lue ? '1px solid var(--bordure)' : '3px solid var(--bleu-institutionnel)',
                }}
              >
                <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                  <div style={{ width: 36, height: 36, borderRadius: 9, background: '#E2EEF9', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Icon size={16} color="var(--bleu-institutionnel)" />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10 }}>
                      <span style={{ fontWeight: 600, fontSize: 14, color: 'var(--ardoise)' }}>{n.titre}</span>
                      <span style={{ fontSize: 12, color: 'var(--ardoise-clair)', whiteSpace: 'nowrap' }}>{tempsRelatif(n.date_creation)}</span>
                    </div>
                    <p style={{ fontSize: 13.5, color: 'var(--ardoise-clair)', marginTop: 4, lineHeight: 1.45 }}>{n.message}</p>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
