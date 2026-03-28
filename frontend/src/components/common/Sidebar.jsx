import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  FiHome, FiBook, FiPlusCircle, FiDollarSign,
  FiBarChart2, FiSettings, FiMessageSquare, FiAward,
} from 'react-icons/fi';

const styles = {
  sidebar: {
    width: '250px', backgroundColor: '#1e1b4b', color: '#e0e7ff',
    minHeight: 'calc(100vh - 64px)', padding: '1.5rem 0',
    display: 'flex', flexDirection: 'column',
  },
  section: { marginBottom: '1.5rem' },
  sectionTitle: {
    fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em',
    color: '#a5b4fc', padding: '0 1.5rem', marginBottom: '0.5rem', fontWeight: 600,
  },
  link: {
    display: 'flex', alignItems: 'center', gap: '0.75rem',
    padding: '0.65rem 1.5rem', color: '#c7d2fe', textDecoration: 'none',
    fontSize: '0.9rem', transition: 'all 0.2s', borderLeft: '3px solid transparent',
  },
  activeLink: {
    backgroundColor: 'rgba(79, 70, 229, 0.3)', color: '#fff',
    borderLeftColor: '#818cf8',
  },
  footer: {
    marginTop: 'auto', padding: '1rem 1.5rem', fontSize: '0.75rem',
    color: '#6366f1', borderTop: '1px solid rgba(255,255,255,0.1)',
  },
};

const instructorLinks = [
  { to: '/instructor', label: 'Dashboard', icon: FiHome, end: true },
  { to: '/instructor/courses', label: 'My Courses', icon: FiBook },
  { to: '/instructor/create', label: 'Create Course', icon: FiPlusCircle },
  { to: '/instructor/earnings', label: 'Earnings', icon: FiDollarSign },
  { to: '/instructor/analytics', label: 'Analytics', icon: FiBarChart2 },
  { to: '/instructor/reviews', label: 'Reviews', icon: FiMessageSquare },
  { to: '/instructor/certificates', label: 'Certificates', icon: FiAward },
  { to: '/instructor/settings', label: 'Settings', icon: FiSettings },
];

const studentLinks = [
  { to: '/learn', label: 'My Learning', icon: FiBook, end: true },
  { to: '/learn/achievements', label: 'Achievements', icon: FiAward },
  { to: '/learn/certificates', label: 'Certificates', icon: FiAward },
];

export default function Sidebar({ variant = 'instructor' }) {
  const links = variant === 'instructor' ? instructorLinks : studentLinks;

  return (
    <aside style={styles.sidebar}>
      <div style={styles.section}>
        <p style={styles.sectionTitle}>
          {variant === 'instructor' ? 'Instructor Panel' : 'Student Panel'}
        </p>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            style={({ isActive }) => ({
              ...styles.link,
              ...(isActive ? styles.activeLink : {}),
            })}
          >
            <link.icon size={18} />
            {link.label}
          </NavLink>
        ))}
      </div>
      <div style={styles.footer}>CourseCraft v1.0</div>
    </aside>
  );
}
