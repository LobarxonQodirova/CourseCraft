import React from 'react';
import { Link } from 'react-router-dom';
import { FiBookOpen, FiGithub, FiTwitter, FiLinkedin } from 'react-icons/fi';

const styles = {
  footer: {
    backgroundColor: '#111827', color: '#9ca3af', padding: '3rem 2rem 1.5rem',
  },
  grid: {
    display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '2rem', maxWidth: '1200px', margin: '0 auto',
  },
  brand: { display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff', fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.75rem' },
  description: { fontSize: '0.85rem', lineHeight: 1.6, marginBottom: '1rem' },
  columnTitle: { color: '#fff', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.75rem' },
  link: { display: 'block', color: '#9ca3af', textDecoration: 'none', fontSize: '0.85rem', marginBottom: '0.5rem' },
  socials: { display: 'flex', gap: '1rem', marginTop: '0.5rem' },
  socialIcon: { color: '#9ca3af', cursor: 'pointer' },
  bottom: {
    maxWidth: '1200px', margin: '2rem auto 0', paddingTop: '1.5rem',
    borderTop: '1px solid #1f2937', display: 'flex',
    justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem',
  },
};

export default function Footer() {
  return (
    <footer style={styles.footer}>
      <div style={styles.grid}>
        <div>
          <div style={styles.brand}><FiBookOpen size={22} /> CourseCraft</div>
          <p style={styles.description}>
            The all-in-one platform for creating, publishing, and selling online courses.
            Empower educators and transform learners worldwide.
          </p>
          <div style={styles.socials}>
            <FiTwitter size={20} style={styles.socialIcon} />
            <FiLinkedin size={20} style={styles.socialIcon} />
            <FiGithub size={20} style={styles.socialIcon} />
          </div>
        </div>

        <div>
          <p style={styles.columnTitle}>Platform</p>
          <Link to="/courses" style={styles.link}>Browse Courses</Link>
          <Link to="/instructor" style={styles.link}>Become an Instructor</Link>
          <a href="#pricing" style={styles.link}>Pricing</a>
          <a href="#enterprise" style={styles.link}>Enterprise</a>
        </div>

        <div>
          <p style={styles.columnTitle}>Resources</p>
          <a href="#help" style={styles.link}>Help Center</a>
          <a href="#blog" style={styles.link}>Blog</a>
          <a href="#guides" style={styles.link}>Teaching Guides</a>
          <a href="#api" style={styles.link}>API Documentation</a>
        </div>

        <div>
          <p style={styles.columnTitle}>Company</p>
          <a href="#about" style={styles.link}>About Us</a>
          <a href="#careers" style={styles.link}>Careers</a>
          <a href="#privacy" style={styles.link}>Privacy Policy</a>
          <a href="#terms" style={styles.link}>Terms of Service</a>
        </div>
      </div>

      <div style={styles.bottom}>
        <span>2024 CourseCraft. All rights reserved.</span>
        <span>Made with passion for education</span>
      </div>
    </footer>
  );
}
