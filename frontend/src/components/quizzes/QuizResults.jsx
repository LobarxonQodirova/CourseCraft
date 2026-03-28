import React from 'react';
import { FiCheckCircle, FiXCircle, FiAward, FiRefreshCw } from 'react-icons/fi';

const styles = {
  container: { maxWidth: '700px', margin: '0 auto', padding: '2rem' },
  header: { textAlign: 'center', marginBottom: '2rem' },
  scoreCircle: {
    width: '140px', height: '140px', borderRadius: '50%',
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', margin: '0 auto 1.5rem', fontSize: '2.5rem',
    fontWeight: 700,
  },
  passed: { backgroundColor: '#dcfce7', color: '#16a34a', border: '4px solid #16a34a' },
  failed: { backgroundColor: '#fee2e2', color: '#ef4444', border: '4px solid #ef4444' },
  scoreLabel: { fontSize: '0.85rem', fontWeight: 500 },
  title: { fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' },
  stats: {
    display: 'flex', justifyContent: 'center', gap: '2rem',
    marginBottom: '2rem', fontSize: '0.9rem', color: '#6b7280',
  },
  statItem: { textAlign: 'center' },
  statValue: { fontSize: '1.5rem', fontWeight: 700, color: '#111827' },
  questionResult: {
    border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1.25rem',
    marginBottom: '1rem',
  },
  questionHeader: {
    display: 'flex', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '0.75rem',
  },
  correct: { color: '#16a34a' },
  incorrect: { color: '#ef4444' },
  explanation: {
    backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0',
    borderRadius: '6px', padding: '0.75rem', marginTop: '0.75rem',
    fontSize: '0.85rem', color: '#15803d',
  },
  actions: {
    display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '2rem',
  },
  btn: {
    padding: '0.6rem 1.5rem', borderRadius: '8px', fontSize: '0.95rem',
    fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem',
  },
  retryBtn: { backgroundColor: '#4f46e5', color: '#fff', border: 'none' },
  continueBtn: { backgroundColor: '#16a34a', color: '#fff', border: 'none' },
};

export default function QuizResults({ result, onRetry, onContinue }) {
  if (!result) return null;

  const { score, passed, correct_count, incorrect_count, total_points, earned_points, question_results } = result;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={{ ...styles.scoreCircle, ...(passed ? styles.passed : styles.failed) }}>
          {Math.round(score)}%
          <span style={styles.scoreLabel}>{passed ? 'Passed!' : 'Not Passed'}</span>
        </div>

        <h2 style={styles.title}>
          {passed ? 'Congratulations!' : 'Keep Trying!'}
        </h2>
        <p style={{ color: '#6b7280' }}>
          {passed
            ? 'You have passed this quiz. Great job!'
            : 'You did not meet the passing score. Review the material and try again.'}
        </p>
      </div>

      <div style={styles.stats}>
        <div style={styles.statItem}>
          <div style={styles.statValue}>{earned_points}/{total_points}</div>
          <div>Points</div>
        </div>
        <div style={styles.statItem}>
          <div style={{ ...styles.statValue, ...styles.correct }}>{correct_count}</div>
          <div>Correct</div>
        </div>
        <div style={styles.statItem}>
          <div style={{ ...styles.statValue, ...styles.incorrect }}>{incorrect_count}</div>
          <div>Incorrect</div>
        </div>
      </div>

      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem' }}>Question Breakdown</h3>

      {question_results?.map((qr, index) => (
        <div key={qr.question_id} style={styles.questionResult}>
          <div style={styles.questionHeader}>
            {qr.correct ? (
              <FiCheckCircle size={20} color="#16a34a" style={{ flexShrink: 0, marginTop: 2 }} />
            ) : (
              <FiXCircle size={20} color="#ef4444" style={{ flexShrink: 0, marginTop: 2 }} />
            )}
            <div>
              <p style={{ fontWeight: 500 }}>Question {index + 1}</p>
              <p style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                {qr.points_earned}/{qr.points_earned + (qr.correct ? 0 : 1)} points
              </p>
            </div>
          </div>
          {qr.explanation && (
            <div style={styles.explanation}>{qr.explanation}</div>
          )}
        </div>
      ))}

      <div style={styles.actions}>
        {!passed && onRetry && (
          <button style={{ ...styles.btn, ...styles.retryBtn }} onClick={onRetry}>
            <FiRefreshCw size={16} /> Try Again
          </button>
        )}
        {onContinue && (
          <button style={{ ...styles.btn, ...styles.continueBtn }} onClick={onContinue}>
            <FiAward size={16} /> Continue
          </button>
        )}
      </div>
    </div>
  );
}
