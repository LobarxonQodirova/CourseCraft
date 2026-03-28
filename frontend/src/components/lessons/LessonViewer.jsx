import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FiCheckCircle, FiFileText, FiDownload, FiMessageSquare } from 'react-icons/fi';
import VideoPlayer from '../common/VideoPlayer';
import { markLessonComplete } from '../../store/slices/progressSlice';

const styles = {
  container: { padding: '1.5rem 2rem' },
  header: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
    marginBottom: '1.5rem',
  },
  title: { fontSize: '1.5rem', fontWeight: 600, color: '#111827' },
  badge: {
    display: 'flex', alignItems: 'center', gap: '0.3rem',
    fontSize: '0.85rem', padding: '0.3rem 0.8rem', borderRadius: '20px',
  },
  completedBadge: { backgroundColor: '#dcfce7', color: '#16a34a' },
  inProgressBadge: { backgroundColor: '#fef3c7', color: '#d97706' },
  content: {
    backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px',
    padding: '1.5rem', marginBottom: '1.5rem', lineHeight: 1.7,
  },
  resources: {
    backgroundColor: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '8px',
    padding: '1.5rem',
  },
  resourceTitle: { fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' },
  resourceItem: {
    display: 'flex', alignItems: 'center', gap: '0.5rem',
    padding: '0.5rem 0', borderBottom: '1px solid #e5e7eb',
    fontSize: '0.9rem', color: '#4f46e5', textDecoration: 'none',
  },
  actions: {
    display: 'flex', gap: '1rem', marginTop: '1.5rem',
  },
  btn: {
    display: 'flex', alignItems: 'center', gap: '0.4rem',
    padding: '0.6rem 1.2rem', borderRadius: '6px', border: 'none',
    cursor: 'pointer', fontSize: '0.9rem', fontWeight: 500,
  },
  completeBtn: { backgroundColor: '#16a34a', color: '#fff' },
  discussBtn: { backgroundColor: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db' },
};

export default function LessonViewer({ lesson, onComplete }) {
  const dispatch = useDispatch();
  const { lessonProgress } = useSelector((state) => state.progress);
  const progress = lessonProgress[lesson?.id];
  const isCompleted = progress?.status === 'completed';

  if (!lesson) return <div style={styles.container}>Select a lesson to begin.</div>;

  const handleMarkComplete = () => {
    dispatch(markLessonComplete(lesson.id));
    if (onComplete) onComplete();
  };

  const handleVideoComplete = () => {
    dispatch(markLessonComplete(lesson.id));
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>{lesson.title}</h2>
          <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>
            {lesson.content_type} {lesson.duration ? `- ${lesson.duration}` : ''}
          </p>
        </div>
        {isCompleted ? (
          <span style={{ ...styles.badge, ...styles.completedBadge }}>
            <FiCheckCircle size={14} /> Completed
          </span>
        ) : progress?.status === 'in_progress' ? (
          <span style={{ ...styles.badge, ...styles.inProgressBadge }}>In Progress</span>
        ) : null}
      </div>

      {lesson.content_type === 'video' && lesson.content?.video_url && (
        <div style={{ marginBottom: '1.5rem' }}>
          <VideoPlayer
            url={lesson.content.video_url}
            lessonId={lesson.id}
            initialPosition={progress?.last_position_seconds || 0}
            onComplete={handleVideoComplete}
          />
        </div>
      )}

      {lesson.content_type === 'article' && lesson.content?.text_content && (
        <div style={styles.content}>
          <div dangerouslySetInnerHTML={{ __html: lesson.content.text_content }} />
        </div>
      )}

      {lesson.content?.resources?.length > 0 && (
        <div style={styles.resources}>
          <h3 style={styles.resourceTitle}>
            <FiFileText style={{ marginRight: '0.5rem' }} /> Resources
          </h3>
          {lesson.content.resources.map((resource, i) => (
            <a key={i} href={resource.url || '#'} style={styles.resourceItem} target="_blank" rel="noopener noreferrer">
              <FiDownload size={14} /> {resource.name || resource.title || `Resource ${i + 1}`}
            </a>
          ))}
        </div>
      )}

      <div style={styles.actions}>
        {!isCompleted && (
          <button style={{ ...styles.btn, ...styles.completeBtn }} onClick={handleMarkComplete}>
            <FiCheckCircle /> Mark as Complete
          </button>
        )}
        <button style={{ ...styles.btn, ...styles.discussBtn }}>
          <FiMessageSquare /> Discussion
        </button>
      </div>
    </div>
  );
}
