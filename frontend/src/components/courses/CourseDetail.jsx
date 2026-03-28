import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  FiStar, FiUsers, FiClock, FiGlobe, FiBarChart,
  FiPlayCircle, FiCheckCircle, FiShoppingCart,
} from 'react-icons/fi';
import { addToCart, enrollInCourse } from '../../store/slices/courseSlice';
import { formatPrice, formatDuration } from '../../utils/formatters';
import ReviewList from '../reviews/ReviewList';

const styles = {
  hero: {
    backgroundColor: '#1e1b4b', color: '#fff', padding: '3rem 2rem',
  },
  heroInner: { maxWidth: '800px' },
  breadcrumb: { fontSize: '0.85rem', color: '#a5b4fc', marginBottom: '1rem' },
  title: { fontSize: '2rem', fontWeight: 700, marginBottom: '0.75rem' },
  subtitle: { fontSize: '1.1rem', color: '#c7d2fe', marginBottom: '1rem', lineHeight: 1.5 },
  meta: { display: 'flex', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.9rem', color: '#e0e7ff' },
  metaItem: { display: 'flex', alignItems: 'center', gap: '0.4rem' },
  content: { maxWidth: '1200px', margin: '0 auto', padding: '2rem', display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' },
  section: { marginBottom: '2rem' },
  sectionTitle: { fontSize: '1.3rem', fontWeight: 600, marginBottom: '1rem', color: '#111827' },
  learnList: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' },
  learnItem: { display: 'flex', gap: '0.5rem', fontSize: '0.9rem', color: '#374151' },
  curriculum: { border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' },
  sectionHeader: {
    display: 'flex', justifyContent: 'space-between', padding: '0.75rem 1rem',
    backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb', fontWeight: 600,
    fontSize: '0.95rem', cursor: 'pointer',
  },
  lessonItem: {
    display: 'flex', alignItems: 'center', gap: '0.5rem',
    padding: '0.6rem 1rem 0.6rem 2rem', fontSize: '0.9rem', color: '#374151',
    borderBottom: '1px solid #f3f4f6',
  },
  sidebar: { position: 'sticky', top: '80px', alignSelf: 'start' },
  priceCard: {
    backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '12px',
    padding: '1.5rem', textAlign: 'center',
  },
  priceTag: { fontSize: '2rem', fontWeight: 700, color: '#111827', marginBottom: '0.5rem' },
  enrollBtn: {
    width: '100%', padding: '0.75rem', backgroundColor: '#4f46e5', color: '#fff',
    border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600,
    cursor: 'pointer', marginBottom: '0.75rem',
  },
  cartBtn: {
    width: '100%', padding: '0.75rem', backgroundColor: '#fff', color: '#4f46e5',
    border: '2px solid #4f46e5', borderRadius: '8px', fontSize: '1rem',
    fontWeight: 600, cursor: 'pointer',
  },
  includes: { textAlign: 'left', marginTop: '1.5rem' },
  includeItem: {
    display: 'flex', alignItems: 'center', gap: '0.5rem',
    padding: '0.4rem 0', fontSize: '0.85rem', color: '#374151',
  },
};

export default function CourseDetail() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { currentCourse: course } = useSelector((state) => state.courses);
  const { isAuthenticated } = useSelector((state) => state.auth);

  if (!course) return null;

  const handleEnroll = () => {
    if (!isAuthenticated) {
      navigate('/');
      return;
    }
    if (course.is_free) {
      dispatch(enrollInCourse(course.slug));
    } else {
      dispatch(addToCart(course));
      navigate('/cart');
    }
  };

  const handleGoToLearn = () => navigate(`/learn/${course.slug}`);

  return (
    <div>
      <div style={styles.hero}>
        <div style={styles.heroInner}>
          <p style={styles.breadcrumb}>
            {course.category?.name || 'Courses'} &gt; {course.title}
          </p>
          <h1 style={styles.title}>{course.title}</h1>
          <p style={styles.subtitle}>{course.subtitle}</p>
          <div style={styles.meta}>
            <span style={styles.metaItem}>
              <FiStar color="#f59e0b" /> {parseFloat(course.average_rating).toFixed(1)} ({course.total_reviews} reviews)
            </span>
            <span style={styles.metaItem}><FiUsers /> {course.total_enrollments} students</span>
            <span style={styles.metaItem}><FiGlobe /> {course.language?.toUpperCase()}</span>
            <span style={styles.metaItem}><FiBarChart /> {course.level}</span>
            {course.total_duration && (
              <span style={styles.metaItem}><FiClock /> {formatDuration(course.total_duration)}</span>
            )}
          </div>
        </div>
      </div>

      <div style={styles.content}>
        <div>
          {course.what_you_learn?.length > 0 && (
            <div style={styles.section}>
              <h2 style={styles.sectionTitle}>What You Will Learn</h2>
              <div style={styles.learnList}>
                {course.what_you_learn.map((item, i) => (
                  <div key={i} style={styles.learnItem}>
                    <FiCheckCircle color="#16a34a" size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {course.sections?.length > 0 && (
            <div style={styles.section}>
              <h2 style={styles.sectionTitle}>
                Course Content - {course.sections.length} sections, {course.total_lessons} lessons
              </h2>
              <div style={styles.curriculum}>
                {course.sections.map((section) => (
                  <div key={section.id}>
                    <div style={styles.sectionHeader}>
                      <span>{section.title}</span>
                      <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                        {section.lessons?.length || 0} lessons
                      </span>
                    </div>
                    {section.lessons?.map((lesson) => (
                      <div key={lesson.id} style={styles.lessonItem}>
                        <FiPlayCircle size={14} color="#4f46e5" />
                        <span style={{ flex: 1 }}>{lesson.title}</span>
                        {lesson.is_preview && (
                          <span style={{ fontSize: '0.75rem', color: '#4f46e5' }}>Preview</span>
                        )}
                        {lesson.duration && (
                          <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                            {formatDuration(lesson.duration)}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>Description</h2>
            <p style={{ lineHeight: 1.7, color: '#374151', whiteSpace: 'pre-wrap' }}>
              {course.description}
            </p>
          </div>

          {course.requirements?.length > 0 && (
            <div style={styles.section}>
              <h2 style={styles.sectionTitle}>Requirements</h2>
              <ul style={{ paddingLeft: '1.5rem', color: '#374151' }}>
                {course.requirements.map((req, i) => (
                  <li key={i} style={{ marginBottom: '0.4rem' }}>{req}</li>
                ))}
              </ul>
            </div>
          )}

          <ReviewList courseSlug={course.slug} />
        </div>

        <div style={styles.sidebar}>
          <div style={styles.priceCard}>
            {course.is_free ? (
              <p style={styles.priceTag}>Free</p>
            ) : (
              <p style={styles.priceTag}>{formatPrice(course.effective_price)}</p>
            )}

            {course.is_enrolled ? (
              <button style={styles.enrollBtn} onClick={handleGoToLearn}>
                Go to Course
              </button>
            ) : (
              <>
                <button style={styles.enrollBtn} onClick={handleEnroll}>
                  {course.is_free ? 'Enroll Now - Free' : 'Buy Now'}
                </button>
                {!course.is_free && (
                  <button style={styles.cartBtn} onClick={() => dispatch(addToCart(course))}>
                    <FiShoppingCart style={{ marginRight: 6 }} /> Add to Cart
                  </button>
                )}
              </>
            )}

            <div style={styles.includes}>
              <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>This course includes:</p>
              <div style={styles.includeItem}><FiPlayCircle /> {course.total_lessons} lessons</div>
              {course.total_duration && (
                <div style={styles.includeItem}><FiClock /> {formatDuration(course.total_duration)} total</div>
              )}
              <div style={styles.includeItem}><FiGlobe /> Full lifetime access</div>
              <div style={styles.includeItem}><FiCheckCircle /> Certificate of completion</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
