import React, { useState } from 'react';
import {
  FiPlayCircle, FiFileText, FiHelpCircle, FiCheckCircle,
  FiChevronDown, FiChevronRight, FiLock, FiDownload,
} from 'react-icons/fi';

const styles = {
  sidebar: {
    width: '350px', backgroundColor: '#f9fafb', borderLeft: '1px solid #e5e7eb',
    overflowY: 'auto', maxHeight: 'calc(100vh - 64px)',
  },
  header: {
    padding: '1rem 1.25rem', borderBottom: '1px solid #e5e7eb',
    fontWeight: 600, fontSize: '1rem', color: '#111827',
  },
  section: { borderBottom: '1px solid #e5e7eb' },
  sectionHeader: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0.75rem 1.25rem', cursor: 'pointer', backgroundColor: '#fff',
    fontWeight: 600, fontSize: '0.9rem', color: '#374151',
  },
  sectionInfo: { fontSize: '0.75rem', color: '#9ca3af', fontWeight: 400 },
  lessonItem: {
    display: 'flex', alignItems: 'center', gap: '0.6rem',
    padding: '0.6rem 1.25rem 0.6rem 2rem', cursor: 'pointer',
    fontSize: '0.85rem', color: '#374151', transition: 'background-color 0.15s',
  },
  activeLesson: { backgroundColor: '#eef2ff', borderLeft: '3px solid #4f46e5' },
  completedLesson: { color: '#16a34a' },
  icon: { flexShrink: 0 },
  lessonTitle: { flex: 1, lineHeight: 1.3 },
  duration: { fontSize: '0.75rem', color: '#9ca3af', flexShrink: 0 },
};

const contentTypeIcons = {
  video: FiPlayCircle,
  article: FiFileText,
  quiz: FiHelpCircle,
  assignment: FiFileText,
  download: FiDownload,
};

export default function LessonList({ sections, currentLessonId, onLessonSelect, lessonProgress = {} }) {
  const [expandedSections, setExpandedSections] = useState(
    sections?.reduce((acc, s) => ({ ...acc, [s.id]: true }), {}) || {}
  );

  const toggleSection = (sectionId) => {
    setExpandedSections((prev) => ({ ...prev, [sectionId]: !prev[sectionId] }));
  };

  if (!sections?.length) return null;

  const totalLessons = sections.reduce((sum, s) => sum + (s.lessons?.length || 0), 0);
  const completedCount = Object.values(lessonProgress).filter((lp) => lp.status === 'completed').length;

  return (
    <div style={styles.sidebar}>
      <div style={styles.header}>
        Course Content
        <p style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: 400, marginTop: '0.2rem' }}>
          {completedCount}/{totalLessons} completed
        </p>
      </div>

      {sections.map((section) => {
        const isExpanded = expandedSections[section.id];
        const sectionCompleted = section.lessons?.every(
          (l) => lessonProgress[l.id]?.status === 'completed'
        );

        return (
          <div key={section.id} style={styles.section}>
            <div style={styles.sectionHeader} onClick={() => toggleSection(section.id)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {isExpanded ? <FiChevronDown size={16} /> : <FiChevronRight size={16} />}
                <span>{section.title}</span>
                {sectionCompleted && <FiCheckCircle size={14} color="#16a34a" />}
              </div>
              <span style={styles.sectionInfo}>
                {section.lessons?.length || 0} lessons
              </span>
            </div>

            {isExpanded && section.lessons?.map((lesson) => {
              const IconComponent = contentTypeIcons[lesson.content_type] || FiPlayCircle;
              const isActive = lesson.id === currentLessonId;
              const isCompleted = lessonProgress[lesson.id]?.status === 'completed';

              return (
                <div
                  key={lesson.id}
                  style={{
                    ...styles.lessonItem,
                    ...(isActive ? styles.activeLesson : {}),
                    ...(isCompleted ? styles.completedLesson : {}),
                  }}
                  onClick={() => onLessonSelect(lesson)}
                >
                  {isCompleted ? (
                    <FiCheckCircle size={16} color="#16a34a" style={styles.icon} />
                  ) : (
                    <IconComponent size={16} color={isActive ? '#4f46e5' : '#9ca3af'} style={styles.icon} />
                  )}
                  <span style={styles.lessonTitle}>{lesson.title}</span>
                  {lesson.duration && (
                    <span style={styles.duration}>{lesson.duration}</span>
                  )}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
