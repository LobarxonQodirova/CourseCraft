import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { FiShoppingCart, FiMenu, FiX, FiSearch, FiUser, FiLogOut, FiBookOpen } from 'react-icons/fi';
import { logout } from '../../store/slices/authSlice';

const styles = {
  nav: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0 2rem', height: '64px', backgroundColor: '#fff',
    borderBottom: '1px solid #e5e7eb', position: 'sticky', top: 0, zIndex: 50,
  },
  logo: {
    fontSize: '1.4rem', fontWeight: 700, color: '#4f46e5',
    textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem',
  },
  searchBar: {
    display: 'flex', alignItems: 'center', gap: '0.5rem',
    backgroundColor: '#f3f4f6', borderRadius: '8px', padding: '0.5rem 1rem',
    flex: 1, maxWidth: '500px', margin: '0 2rem',
  },
  searchInput: {
    border: 'none', backgroundColor: 'transparent', outline: 'none',
    flex: 1, fontSize: '0.9rem',
  },
  navLinks: { display: 'flex', alignItems: 'center', gap: '1rem' },
  link: {
    textDecoration: 'none', color: '#374151', fontSize: '0.9rem',
    fontWeight: 500, padding: '0.5rem 0.75rem', borderRadius: '6px',
    transition: 'background-color 0.2s',
  },
  cartBadge: {
    position: 'relative', display: 'flex', alignItems: 'center',
  },
  badge: {
    position: 'absolute', top: '-6px', right: '-6px',
    backgroundColor: '#ef4444', color: '#fff', fontSize: '0.65rem',
    fontWeight: 700, borderRadius: '50%', width: '18px', height: '18px',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  btn: {
    padding: '0.5rem 1.2rem', borderRadius: '6px', border: 'none',
    cursor: 'pointer', fontSize: '0.9rem', fontWeight: 600,
  },
  btnPrimary: { backgroundColor: '#4f46e5', color: '#fff' },
  btnOutline: { backgroundColor: 'transparent', color: '#4f46e5', border: '1px solid #4f46e5' },
  dropdown: {
    position: 'absolute', top: '100%', right: 0,
    backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px',
    padding: '0.5rem 0', minWidth: '200px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  dropdownItem: {
    display: 'flex', alignItems: 'center', gap: '0.5rem',
    padding: '0.6rem 1rem', color: '#374151', textDecoration: 'none',
    fontSize: '0.9rem', cursor: 'pointer', border: 'none', backgroundColor: 'transparent',
    width: '100%', textAlign: 'left',
  },
};

export default function Navbar() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const { cart } = useSelector((state) => state.courses);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/courses?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleLogout = () => {
    dispatch(logout());
    setShowDropdown(false);
    navigate('/');
  };

  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.logo}>
        <FiBookOpen size={24} /> CourseCraft
      </Link>

      <form onSubmit={handleSearch} style={styles.searchBar}>
        <FiSearch size={18} color="#9ca3af" />
        <input
          type="text"
          placeholder="Search for courses..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={styles.searchInput}
        />
      </form>

      <div style={styles.navLinks}>
        <Link to="/courses" style={styles.link}>Explore</Link>

        {isAuthenticated && user?.role === 'creator' && (
          <Link to="/instructor" style={styles.link}>Teach</Link>
        )}

        <Link to="/cart" style={{ ...styles.link, ...styles.cartBadge }}>
          <FiShoppingCart size={20} />
          {cart.length > 0 && <span style={styles.badge}>{cart.length}</span>}
        </Link>

        {isAuthenticated ? (
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              style={{ ...styles.btn, ...styles.btnOutline, display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            >
              <FiUser size={16} /> {user?.full_name?.split(' ')[0] || 'Account'}
            </button>
            {showDropdown && (
              <div style={styles.dropdown}>
                <Link to="/learn" style={styles.dropdownItem} onClick={() => setShowDropdown(false)}>
                  <FiBookOpen size={16} /> My Learning
                </Link>
                <Link to="/profile" style={styles.dropdownItem} onClick={() => setShowDropdown(false)}>
                  <FiUser size={16} /> Profile
                </Link>
                <button onClick={handleLogout} style={styles.dropdownItem}>
                  <FiLogOut size={16} /> Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={() => navigate('/courses')}
            style={{ ...styles.btn, ...styles.btnPrimary }}
          >
            Get Started
          </button>
        )}
      </div>
    </nav>
  );
}
