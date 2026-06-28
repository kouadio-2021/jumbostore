import React, { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Radar, Building2, FileStack, Scale,
  Receipt, Bell, Menu, X
} from 'lucide-react'
import { getNotifications } from '../services/api.js'
import './Layout.css'

const NAV_ITEMS = [
  { to: '/tableau-de-bord', label: 'Tableau de bord', icon: LayoutDashboard },
  { to: '/appels-offres', label: 'Veille marchés', icon: Radar },
  { to: '/entreprise', label: 'Profil entreprise', icon: Building2 },
  { to: '/soumissions', label: 'Soumissions', icon: FileStack },
  { to: '/comparateur', label: 'Comparateur de prix', icon: Scale },
  { to: '/facturation', label: 'Facturation', icon: Receipt },
]

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [notifNonLues, setNotifNonLues] = useState(0)

  useEffect(() => {
    getNotifications(true)
      .then((res) => setNotifNonLues(res.data.length))
      .catch(() => setNotifNonLues(0))
  }, [])

  return (
    <div className="layout">
      <aside className={`sidebar ${sidebarOpen ? 'sidebar--open' : ''}`}>
        <div className="sidebar__brand">
          <div className="sidebar__logo">JS</div>
          <div>
            <div className="sidebar__brand-name">JUMBOSTORE</div>
            <div className="sidebar__brand-sub">Jumbo Store SARL</div>
          </div>
          <button className="sidebar__close" onClick={() => setSidebarOpen(false)} aria-label="Fermer le menu">
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar__nav">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <Icon size={18} strokeWidth={2} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <NavLink
          to="/notifications"
          className={({ isActive }) => `sidebar__notif ${isActive ? 'sidebar__link--active' : ''}`}
          onClick={() => setSidebarOpen(false)}
        >
          <Bell size={18} strokeWidth={2} />
          <span>Notifications</span>
          {notifNonLues > 0 && <span className="sidebar__badge">{notifNonLues}</span>}
        </NavLink>

        <div className="sidebar__footer">
          <div className="sidebar__user-avatar">KG</div>
          <div>
            <div className="sidebar__user-name">Kouadio Gildas</div>
            <div className="sidebar__user-role">Directeur IT &amp; Amélioration Continue</div>
          </div>
        </div>
      </aside>

      {sidebarOpen && <div className="sidebar__overlay" onClick={() => setSidebarOpen(false)} />}

      <div className="layout__main">
        <header className="topbar">
          <button className="topbar__menu-btn" onClick={() => setSidebarOpen(true)} aria-label="Ouvrir le menu">
            <Menu size={22} />
          </button>
          <div className="topbar__spacer" />
        </header>
        <main className="layout__content">{children}</main>
      </div>
    </div>
  )
}
