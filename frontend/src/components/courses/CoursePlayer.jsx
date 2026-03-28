import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FiCheckCircle, FiLock, FiPlayCircle } from 'react-icons/fi';
import VideoPlayer from '../common/VideoPlayer';
import LessonList from '../lessons/LessonList';
import { markLessonComplete, fetchCourseProgress } from '../../store/slices/progressSlice';

const styles = {
  container: { display: 'flex', minHeight: 'calc(100vh - 64px)' },
  mainArea: { flex: 1, display: 'flex', flexDirection: 'column' },
  videoSection: { backgroundColor: '#000', padding: '0' },
  lessonInfo: { padding: '1.5rem 2rem' },
  lessonTitle: { fontSize: '1.4rem', fontWeight: 600, marginBottom: '0.5rem' },
  lessonMeta: { display: 'flex', gap: '1rem', color: '#6b7280', fontSize: '0.9rem', marginBottom: '1rem' },
  controls: {
    display: 'flex', gap: '1rem', padding: '1rem 2rem',
    borderTop: '1px solid #e5e7eb',
  },
  btn: {
    padding: '0.5rem 1.2rem', borderRadius: '6px', border: '1px solid #d1d5db',
    backgroundColor: '#fff', cursor: 'pointer', fontSize: '0.9rem',
    display: 'flex', alignItems: 'center', gap: '0.4rem',
  },
  completeBtn: {
    padding: '0.5rem 1.2rem', borderRadius: '6px', border: 'none',
    backgroundColor: '#16a34a', color: '#fff', cursor: 'pointer',
    fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem',
  },
  completedBadge: {
    display: 'flex', alignItems: 'center', gap: '0.4rem',
    color: '#16a34a', fontWeight: 600, fontSize: '0.9rem',
  },
  content: { padding: '1.5rem 2rem', borderTop: '1px solid #e5e7eb' },
  progressBar: {
    height: '4px', backgroundColor: '#e5e7eb', borderRadius: '2px',
    margin: '0.5rem 2rem',
  },
  progressFill: {
    height: '100%', backgroundColor: '#4f46e5', borderRadius: '2px',
    transition: 'width 0.5s',
  },
};

export default function CoursePlayer({ course }) {
  const dispatch = useDispatch();
  const { lessonProgress, courseProgress } = useSelector((state) => state.progress);
  const [currentLesson, setCurrentLesson] = useState(null);

  useEffect(() => {
    if (course?.sections?.length > 0) {
      const firstLesson = course.sections[0]?.lessons?.[0];
      if (firstLesson) setCurrentLesson(firstLesson);
    }
    if (course?.slug) {
      dispatch(fetchCourseProgress(course.slug));
    }
  }, [course, dispatch]);

  const handleLessonSelect = (lesson) => setCurrentLesson(lesson);

  const handleMarkComplete = () => {
    if (currentLesson) {
      dispatch(markLessonComplete(currentLesson.id));
    }
  };

  const handleVideoComplete = () => {
    if (currentLesson) {
      dispatch(markLessonComplete(currentLesson.id));
    }
  };

  const navigateLesson = (direction) => {
    if (!course?.sections || !currentLesson) return;
    const allLessons = course.sections.flatMap((s) => s.lessons || []);
    const currentIndex = allLessons.findIndex((l) => l.id === currentLesson.id);
    const nextIndex = currentIndex + direction;
    if (nextIndex >= 0 && nextIndex < allLessons.length) {
      setCurrentLesson(allLessons[nextIndex]);
    }
  };

  const isLessonCompleted = (lessonId) => {
    return lessonProgress[lessonId]?.status === 'completed';
  };

  if (!currentLesson) return <div style={{ padding: '2rem' }}>Loading course content...</div>;

  const progressPercent = courseProgress?.progress_percent || 0;

  return (
    <div style={styles.container}>
      <div style={styles.mainArea}>
        <div style={styles.progressBar}>
          <div style={{ ...styles.progressFill, width: `${progressPercent}%` }} />
        </div>

        {currentLesson.content_type === 'video' && currentLesson.content?.video_url ? (
          <div style={styles.videoSection}>
            <VideoPlayer
              url={currentLesson.content.video_url}
              lessonId={currentLesson.id}
              initialPosition={lessonProgress[currentLesson.id]?.last_position_seconds || 0}
              onComplete={handleVideoComplete}
            />
          </div>
        ) : (
          <div style={{ ...styles.content, minHeight: '400px' }}>
            <div dangerouslySetInnerHTML={{ __html: currentLesson.content?.text_content || '<p>No content available.</p>' }} />
          </div>
        )}

        <div style={styles.lessonInfo}>
          <h2 style={styles.lessonTitle}>{currentLesson.title}</h2>
          <div style={styles.lessonMeta}>
            <span>{currentLesson.content_type}</span>
            {currentLesson.duration && <span>{currentLesson.duration}</span>}
          </div>
        </div>

        <div style={styles.controls}>
          <button style={styles.btn} onClick={() => navigateLesson(-1)}>Previous</button>
          <button style={styles.btn} onClick={() => navigateLesson(1)}>Next Lesson</button>
          {isLessonCompleted(currentLesson.id) ? (
            <span style={styles.completedBadge}>
              <FiCheckCircle /> Completed
            </span>
          ) : (
            <button style={styles.completeBtn} onClick={handleMarkComplete}>
              <FiCheckCircle /> Mark Complete
            </button>
          )}
        </div>
      </div>

      <LessonList
        sections={course.sections}
        currentLessonId={currentLesson.id}
        onLessonSelect={handleLessonSelect}
        lessonProgress={lessonProgress}
      />
    </div>
  );
}
