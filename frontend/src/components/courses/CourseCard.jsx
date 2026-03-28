import React from 'react';
import { Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { FiStar, FiUsers, FiClock, FiShoppingCart } from 'react-icons/fi';
import { addToCart } from '../../store/slices/courseSlice';
import { formatPrice, formatDuration } from '../../utils/formatters';

const styles = {
  card: {
    backgroundColor: '#fff', borderRadius: '12px', overflow: 'hidden',
    border: '1px solid #e5e7eb', transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer',
  },
  thumbnail: {
    width: '100%', height: '180px', objectFit: 'cover',
    backgroundColor: '#f3f4f6',
  },
  body: { padding: '1rem' },
  category: {
    fontSize: '0.75rem', color: '#4f46e5', fontWeight: 600,
    textTransform: 'uppercase', marginBottom: '0.4rem',
  },
  title: {
    fontSize: '1rem', fontWeight: 600, color: '#111827',
    lineHeight: 1.3, marginBottom: '0.4rem',
    display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  instructor: { fontSize: '0.8rem', color: '#6b7280', marginBottom: '0.5rem' },
  stats: {
    display: 'flex', alignItems: 'center', gap: '1rem',
    fontSize: '0.8rem', color: '#6b7280', marginBottom: '0.75rem',
  },
  statItem: { display: 'flex', alignItems: 'center', gap: '0.25rem' },
  rating: { color: '#f59e0b', fontWeight: 600 },
  footer: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    paddingTop: '0.75rem', borderTop: '1px solid #f3f4f6',
  },
  price: { fontSize: '1.1rem', fontWeight: 700, color: '#111827' },
  originalPrice: {
    fontSize: '0.85rem', color: '#9ca3af', textDecoration: 'line-through',
    marginLeft: '0.5rem',
  },
  freeTag: {
    backgroundColor: '#dcfce7', color: '#16a34a', padding: '0.2rem 0.6rem',
    borderRadius: '4px', fontWeight: 600, fontSize: '0.85rem',
  },
  cartBtn: {
    backgroundColor: '#4f46e5', color: '#fff', border: 'none',
    borderRadius: '6px', padding: '0.4rem 0.8rem', cursor: 'pointer',
    display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem',
  },
  level: {
    fontSize: '0.7rem', padding: '0.15rem 0.5rem', borderRadius: '4px',
    backgroundColor: '#f3f4f6', color: '#6b7280', fontWeight: 500,
  },
};

export default function CourseCard({ course }) {
  const dispatch = useDispatch();

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dispatch(addToCart(course));
  };

  return (
    <Link to={`/courses/${course.slug}`} style={{ textDecoration: 'none' }}>
      <div style={styles.card}>
        <img
          src={course.thumbnail || 'https://via.placeholder.com/400x200?text=Course'}
          alt={course.title}
          style={styles.thumbnail}
        />
        <div style={styles.body}>
          <p style={styles.category}>{course.category_name || 'General'}</p>
          <h3 style={styles.title}>{course.title}</h3>
          <p style={styles.instructor}>
            {course.instructor?.display_name || 'Unknown Instructor'}
          </p>

          <div style={styles.stats}>
            <span style={styles.statItem}>
              <FiStar size={14} style={{ color: '#f59e0b' }} />
              <span style={styles.rating}>
                {parseFloat(course.average_rating).toFixed(1)}
              </span>
              <span>({course.total_reviews})</span>
            </span>
            <span style={styles.statItem}>
              <FiUsers size={14} /> {course.total_enrollments}
            </span>
            {course.total_duration && (
              <span style={styles.statItem}>
                <FiClock size={14} /> {formatDuration(course.total_duration)}
              </span>
            )}
          </div>

          <div style={styles.footer}>
            {course.is_free ? (
              <span style={styles.freeTag}>Free</span>
            ) : (
              <div style={{ display: 'flex', alignItems: 'baseline' }}>
                <span style={styles.price}>{formatPrice(course.effective_price)}</span>
                {course.discount_price && (
                  <span style={styles.originalPrice}>{formatPrice(course.price)}</span>
                )}
              </div>
            )}
            {!course.is_free && (
              <button style={styles.cartBtn} onClick={handleAddToCart}>
                <FiShoppingCart size={14} /> Add
              </button>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
