import React, { useCallback, useEffect, useRef, useState } from 'react';
import ReactPlayer from 'react-player';
import { useDispatch } from 'react-redux';
import { updateLessonProgress } from '../../store/slices/progressSlice';

const styles = {
  wrapper: {
    position: 'relative', backgroundColor: '#000', borderRadius: '8px',
    overflow: 'hidden', aspectRatio: '16/9',
  },
  controls: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0.5rem 1rem', backgroundColor: '#1f2937', color: '#fff',
    fontSize: '0.85rem',
  },
  progressBar: {
    width: '100%', height: '4px', backgroundColor: '#374151',
    borderRadius: '2px', cursor: 'pointer', position: 'relative',
  },
  progressFill: {
    height: '100%', backgroundColor: '#4f46e5', borderRadius: '2px',
    transition: 'width 0.3s',
  },
  btn: {
    backgroundColor: 'transparent', border: 'none', color: '#fff',
    cursor: 'pointer', padding: '0.25rem 0.5rem', fontSize: '0.85rem',
  },
  speedSelect: {
    backgroundColor: '#374151', color: '#fff', border: 'none',
    borderRadius: '4px', padding: '0.2rem 0.4rem', fontSize: '0.8rem',
  },
};

export default function VideoPlayer({ url, lessonId, initialPosition = 0, onComplete }) {
  const dispatch = useDispatch();
  const playerRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [played, setPlayed] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [watchTime, setWatchTime] = useState(0);
  const lastSaveRef = useRef(Date.now());

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const saveProgress = useCallback(() => {
    if (!lessonId || !duration) return;
    const currentPosition = Math.floor(played * duration);
    dispatch(updateLessonProgress({
      lessonId,
      progressData: {
        watch_time_seconds: watchTime,
        last_position_seconds: currentPosition,
        status: played >= 0.9 ? 'completed' : 'in_progress',
      },
    }));
  }, [dispatch, lessonId, played, duration, watchTime]);

  const handleProgress = (state) => {
    setPlayed(state.played);
    setWatchTime((prev) => prev + 1);

    if (Date.now() - lastSaveRef.current > 30000) {
      saveProgress();
      lastSaveRef.current = Date.now();
    }

    if (state.played >= 0.95 && onComplete) {
      onComplete();
    }
  };

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const fraction = (e.clientX - rect.left) / rect.width;
    playerRef.current?.seekTo(fraction, 'fraction');
    setPlayed(fraction);
  };

  useEffect(() => {
    return () => { saveProgress(); };
  }, [saveProgress]);

  useEffect(() => {
    if (initialPosition > 0 && playerRef.current && duration > 0) {
      playerRef.current.seekTo(initialPosition / duration, 'fraction');
    }
  }, [initialPosition, duration]);

  return (
    <div>
      <div style={styles.wrapper}>
        <ReactPlayer
          ref={playerRef}
          url={url}
          width="100%"
          height="100%"
          playing={playing}
          playbackRate={playbackRate}
          onProgress={handleProgress}
          onDuration={setDuration}
          onPause={() => { setPlaying(false); saveProgress(); }}
          onEnded={() => { setPlaying(false); saveProgress(); }}
          controls={false}
          config={{
            youtube: { playerVars: { modestbranding: 1, rel: 0 } },
            vimeo: { playerOptions: { byline: false, portrait: false } },
          }}
        />
      </div>

      <div style={styles.controls}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button style={styles.btn} onClick={() => setPlaying(!playing)}>
            {playing ? 'Pause' : 'Play'}
          </button>
          <span>{formatTime(played * duration)} / {formatTime(duration)}</span>
        </div>

        <div style={{ flex: 1, margin: '0 1rem' }} onClick={handleSeek}>
          <div style={styles.progressBar}>
            <div style={{ ...styles.progressFill, width: `${played * 100}%` }} />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <select
            value={playbackRate}
            onChange={(e) => setPlaybackRate(parseFloat(e.target.value))}
            style={styles.speedSelect}
          >
            {[0.5, 0.75, 1, 1.25, 1.5, 2].map((speed) => (
              <option key={speed} value={speed}>{speed}x</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
