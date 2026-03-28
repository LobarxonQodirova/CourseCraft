import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { FiClock, FiCheckCircle, FiXCircle, FiAlertCircle } from 'react-icons/fi';
import quizApi from '../../api/quizApi';

const styles = {
  container: { maxWidth: '800px', margin: '0 auto', padding: '2rem' },
  header: { marginBottom: '2rem' },
  title: { fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' },
  meta: { display: 'flex', gap: '1.5rem', color: '#6b7280', fontSize: '0.9rem' },
  metaItem: { display: 'flex', alignItems: 'center', gap: '0.3rem' },
  question: {
    backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px',
    padding: '1.5rem', marginBottom: '1.5rem',
  },
  questionNumber: { fontSize: '0.8rem', color: '#4f46e5', fontWeight: 600, marginBottom: '0.5rem' },
  questionText: { fontSize: '1.05rem', fontWeight: 500, marginBottom: '1rem', lineHeight: 1.5 },
  answers: { display: 'flex', flexDirection: 'column', gap: '0.5rem' },
  answer: {
    display: 'flex', alignItems: 'center', gap: '0.75rem',
    padding: '0.75rem 1rem', border: '2px solid #e5e7eb', borderRadius: '8px',
    cursor: 'pointer', transition: 'all 0.15s', fontSize: '0.95rem',
  },
  selectedAnswer: { borderColor: '#4f46e5', backgroundColor: '#eef2ff' },
  submitBtn: {
    padding: '0.75rem 2rem', backgroundColor: '#4f46e5', color: '#fff',
    border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600,
    cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem',
    margin: '2rem auto 0',
  },
  timer: {
    position: 'fixed', top: '80px', right: '2rem',
    backgroundColor: '#1e1b4b', color: '#fff', padding: '0.6rem 1.2rem',
    borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.5rem',
    fontWeight: 600, fontSize: '1.1rem',
  },
  points: { fontSize: '0.8rem', color: '#9ca3af', marginTop: '0.3rem' },
};

export default function QuizView({ quizId, onComplete }) {
  const [quiz, setQuiz] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [responses, setResponses] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const startQuiz = async () => {
      try {
        const { data } = await quizApi.startQuiz(quizId);
        setQuiz(data.quiz);
        setAttempt(data.attempt);
        if (data.quiz.time_limit_minutes) {
          setTimeLeft(data.quiz.time_limit_minutes * 60);
        }
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Failed to start quiz.');
      }
    };
    startQuiz();
  }, [quizId]);

  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleSelectAnswer = (questionId, answerId) => {
    const question = quiz.questions.find((q) => q.id === questionId);
    if (question.question_type === 'multiple_choice') {
      setResponses((prev) => {
        const current = prev[questionId] || [];
        const updated = current.includes(answerId)
          ? current.filter((id) => id !== answerId)
          : [...current, answerId];
        return { ...prev, [questionId]: updated };
      });
    } else {
      setResponses((prev) => ({ ...prev, [questionId]: [answerId] }));
    }
  };

  const handleSubmit = async () => {
    if (submitting) return;
    setSubmitting(true);
    try {
      const { data } = await quizApi.submitQuiz(quizId, attempt.id, responses);
      if (onComplete) onComplete(data);
    } catch (error) {
      toast.error('Failed to submit quiz.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTimeLeft = () => {
    if (timeLeft === null) return '';
    const mins = Math.floor(timeLeft / 60);
    const secs = timeLeft % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!quiz) return <div style={styles.container}>Loading quiz...</div>;

  return (
    <div style={styles.container}>
      {timeLeft !== null && (
        <div style={{ ...styles.timer, color: timeLeft < 60 ? '#ef4444' : '#fff' }}>
          <FiClock /> {formatTimeLeft()}
        </div>
      )}

      <div style={styles.header}>
        <h1 style={styles.title}>{quiz.title}</h1>
        {quiz.description && <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>{quiz.description}</p>}
        <div style={styles.meta}>
          <span style={styles.metaItem}>{quiz.total_questions} questions</span>
          <span style={styles.metaItem}>{quiz.total_points} points</span>
          <span style={styles.metaItem}>Pass: {quiz.passing_score}%</span>
          {quiz.time_limit_minutes && (
            <span style={styles.metaItem}><FiClock /> {quiz.time_limit_minutes} min</span>
          )}
        </div>
      </div>

      {quiz.questions?.map((question, index) => (
        <div key={question.id} style={styles.question}>
          <p style={styles.questionNumber}>
            Question {index + 1} of {quiz.total_questions}
            {question.question_type === 'multiple_choice' && ' (Select all that apply)'}
          </p>
          <p style={styles.questionText}>{question.text}</p>
          <p style={styles.points}>{question.points} point{question.points !== 1 ? 's' : ''}</p>

          <div style={styles.answers}>
            {question.answers?.map((answer) => {
              const isSelected = (responses[question.id] || []).includes(answer.id);
              return (
                <div
                  key={answer.id}
                  style={{ ...styles.answer, ...(isSelected ? styles.selectedAnswer : {}) }}
                  onClick={() => handleSelectAnswer(question.id, answer.id)}
                >
                  <input
                    type={question.question_type === 'multiple_choice' ? 'checkbox' : 'radio'}
                    checked={isSelected}
                    onChange={() => {}}
                    style={{ accentColor: '#4f46e5' }}
                  />
                  <span>{answer.text}</span>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      <button style={styles.submitBtn} onClick={handleSubmit} disabled={submitting}>
        <FiCheckCircle /> {submitting ? 'Submitting...' : 'Submit Quiz'}
      </button>
    </div>
  );
}
