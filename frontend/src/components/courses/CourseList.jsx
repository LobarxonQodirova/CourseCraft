import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCourses, setFilters } from '../../store/slices/courseSlice';
import CourseCard from './CourseCard';

const styles = {
  container: { maxWidth: '1200px', margin: '0 auto', padding: '2rem' },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem',
  },
  filters: {
    display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap',
    alignItems: 'center',
  },
  select: {
    padding: '0.5rem 1rem', borderRadius: '6px', border: '1px solid #d1d5db',
    fontSize: '0.9rem', backgroundColor: '#fff', cursor: 'pointer',
  },
  resultCount: {
    fontSize: '0.9rem', color: '#6b7280', marginBottom: '1rem',
  },
  loading: {
    textAlign: 'center', padding: '3rem', color: '#6b7280', fontSize: '1.1rem',
  },
  empty: {
    textAlign: 'center', padding: '4rem', color: '#9ca3af',
  },
  pagination: {
    display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '2rem',
  },
  pageBtn: {
    padding: '0.5rem 1.2rem', borderRadius: '6px', border: '1px solid #d1d5db',
    backgroundColor: '#fff', cursor: 'pointer', fontSize: '0.9rem',
  },
};

export default function CourseList({ categorySlug, searchQuery }) {
  const dispatch = useDispatch();
  const { list, loading, pagination, filters } = useSelector((state) => state.courses);

  useEffect(() => {
    const params = { ...filters };
    if (categorySlug) params.category__slug = categorySlug;
    if (searchQuery) params.search = searchQuery;
    dispatch(fetchCourses(params));
  }, [dispatch, filters, categorySlug, searchQuery]);

  const handleFilterChange = (key, value) => {
    dispatch(setFilters({ [key]: value }));
  };

  if (loading) {
    return <div style={styles.loading}>Loading courses...</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.filters}>
        <select
          value={filters.level}
          onChange={(e) => handleFilterChange('level', e.target.value)}
          style={styles.select}
        >
          <option value="">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
          <option value="all_levels">All Levels</option>
        </select>

        <select
          value={filters.is_free}
          onChange={(e) => handleFilterChange('is_free', e.target.value)}
          style={styles.select}
        >
          <option value="">All Prices</option>
          <option value="true">Free</option>
          <option value="false">Paid</option>
        </select>

        <select
          value={filters.ordering}
          onChange={(e) => handleFilterChange('ordering', e.target.value)}
          style={styles.select}
        >
          <option value="-created_at">Newest</option>
          <option value="-average_rating">Highest Rated</option>
          <option value="-total_enrollments">Most Popular</option>
          <option value="price">Price: Low to High</option>
          <option value="-price">Price: High to Low</option>
        </select>
      </div>

      {pagination.count > 0 && (
        <p style={styles.resultCount}>{pagination.count} courses found</p>
      )}

      {list.length === 0 ? (
        <div style={styles.empty}>
          <h3>No courses found</h3>
          <p>Try adjusting your filters or search terms.</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {list.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}

      {(pagination.next || pagination.previous) && (
        <div style={styles.pagination}>
          {pagination.previous && (
            <button style={styles.pageBtn} onClick={() => dispatch(fetchCourses({ page: 'prev' }))}>
              Previous
            </button>
          )}
          {pagination.next && (
            <button style={styles.pageBtn} onClick={() => dispatch(fetchCourses({ page: 'next' }))}>
              Next
            </button>
          )}
        </div>
      )}
    </div>
  );
}
