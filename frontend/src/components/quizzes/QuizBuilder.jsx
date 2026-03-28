import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { FiPlus, FiTrash2, FiSave, FiCheck } from 'react-icons/fi';
import quizApi from '../../api/quizApi';

const styles = {
  container: { maxWidth: '800px', margin: '0 auto', padding: '2rem' },
  title: { fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '1.5rem' },
  group: { display: 'flex', flexDirection: 'column', gap: '0.4rem' },
  label: { fontSize: '0.9rem', fontWeight: 600, color: '#374151' },
  input: { padding: '0.6rem', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '0.95rem' },
  row: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' },
  questionCard: {
    border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1.5rem',
    backgroundColor: '#fafafa',
  },
  questionHeader: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem',
  },
  answerRow: {
    display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem',
  },
  checkbox: { width: '20px', height: '20px', accentColor: '#16a34a', cursor: 'pointer' },
  answerInput: { flex: 1, padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db', fontSize: '0.9rem' },
  addBtn: {
    display: 'flex', alignItems: 'center', gap: '0.3rem',
    padding: '0.5rem 1rem', backgroundColor: '#f3f4f6', border: '1px solid #d1d5db',
    borderRadius: '6px', cursor: 'pointer', fontSize: '0.9rem',
  },
  removeBtn: { backgroundColor: 'transparent', border: 'none', cursor: 'pointer', color: '#ef4444' },
  saveBtn: {
    padding: '0.75rem 2rem', backgroundColor: '#4f46e5', color: '#fff',
    border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600,
    cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem',
  },
  select: { padding: '0.6rem', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '0.9rem' },
};

const emptyQuestion = () => ({
  text: '', question_type: 'single_choice', explanation: '', points: 1, order: 0,
  answers: [
    { text: '', is_correct: true, order: 0 },
    { text: '', is_correct: false, order: 1 },
  ],
});

export default function QuizBuilder({ lessonId, existingQuiz, onSave }) {
  const [quizData, setQuizData] = useState(existingQuiz || {
    title: '', description: '', time_limit_minutes: null,
    passing_score: 70, max_attempts: 3, shuffle_questions: false,
  });
  const [questions, setQuestions] = useState(existingQuiz?.questions || [emptyQuestion()]);
  const [saving, setSaving] = useState(false);

  const updateQuestion = (index, field, value) => {
    setQuestions((prev) => prev.map((q, i) => i === index ? { ...q, [field]: value } : q));
  };

  const updateAnswer = (qIndex, aIndex, field, value) => {
    setQuestions((prev) => prev.map((q, qi) => {
      if (qi !== qIndex) return q;
      const answers = q.answers.map((a, ai) => {
        if (ai !== aIndex) {
          if (field === 'is_correct' && value && q.question_type === 'single_choice') {
            return { ...a, is_correct: false };
          }
          return a;
        }
        return { ...a, [field]: value };
      });
      return { ...q, answers };
    }));
  };

  const addQuestion = () => setQuestions((prev) => [...prev, emptyQuestion()]);

  const removeQuestion = (index) => {
    if (questions.length <= 1) return;
    setQuestions((prev) => prev.filter((_, i) => i !== index));
  };

  const addAnswer = (qIndex) => {
    setQuestions((prev) => prev.map((q, i) => {
      if (i !== qIndex) return q;
      return { ...q, answers: [...q.answers, { text: '', is_correct: false, order: q.answers.length }] };
    }));
  };

  const removeAnswer = (qIndex, aIndex) => {
    setQuestions((prev) => prev.map((q, qi) => {
      if (qi !== qIndex || q.answers.length <= 2) return q;
      return { ...q, answers: q.answers.filter((_, ai) => ai !== aIndex) };
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      let quiz;
      if (existingQuiz?.id) {
        const { data } = await quizApi.updateQuiz(existingQuiz.id, quizData);
        quiz = data;
      } else {
        const { data } = await quizApi.createQuiz({ ...quizData, lesson: lessonId });
        quiz = data;
      }

      for (const [i, question] of questions.entries()) {
        await quizApi.createQuestion(quiz.id, { ...question, quiz: quiz.id, order: i });
      }

      toast.success('Quiz saved successfully!');
      if (onSave) onSave(quiz);
    } catch (error) {
      toast.error('Failed to save quiz.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>{existingQuiz ? 'Edit Quiz' : 'Create Quiz'}</h2>
      <div style={styles.form}>
        <div style={styles.group}>
          <label style={styles.label}>Quiz Title</label>
          <input value={quizData.title} onChange={(e) => setQuizData({ ...quizData, title: e.target.value })} style={styles.input} placeholder="e.g., Module 1 Knowledge Check" />
        </div>

        <div style={styles.row}>
          <div style={styles.group}>
            <label style={styles.label}>Time Limit (min)</label>
            <input type="number" value={quizData.time_limit_minutes || ''} onChange={(e) => setQuizData({ ...quizData, time_limit_minutes: e.target.value ? parseInt(e.target.value) : null })} style={styles.input} placeholder="No limit" />
          </div>
          <div style={styles.group}>
            <label style={styles.label}>Passing Score (%)</label>
            <input type="number" value={quizData.passing_score} onChange={(e) => setQuizData({ ...quizData, passing_score: parseInt(e.target.value) })} style={styles.input} min="1" max="100" />
          </div>
          <div style={styles.group}>
            <label style={styles.label}>Max Attempts</label>
            <input type="number" value={quizData.max_attempts} onChange={(e) => setQuizData({ ...quizData, max_attempts: parseInt(e.target.value) })} style={styles.input} min="0" />
          </div>
        </div>

        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginTop: '1rem' }}>Questions</h3>

        {questions.map((question, qIndex) => (
          <div key={qIndex} style={styles.questionCard}>
            <div style={styles.questionHeader}>
              <span style={{ fontWeight: 600 }}>Question {qIndex + 1}</span>
              <button style={styles.removeBtn} onClick={() => removeQuestion(qIndex)}>
                <FiTrash2 size={18} />
              </button>
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.75rem' }}>
              <select value={question.question_type} onChange={(e) => updateQuestion(qIndex, 'question_type', e.target.value)} style={{ ...styles.select, flex: 1 }}>
                <option value="single_choice">Single Choice</option>
                <option value="multiple_choice">Multiple Choice</option>
                <option value="true_false">True / False</option>
              </select>
              <input type="number" value={question.points} onChange={(e) => updateQuestion(qIndex, 'points', parseInt(e.target.value))} style={{ ...styles.input, width: '80px' }} min="1" placeholder="Points" />
            </div>

            <input value={question.text} onChange={(e) => updateQuestion(qIndex, 'text', e.target.value)} style={{ ...styles.input, width: '100%', marginBottom: '0.75rem' }} placeholder="Enter question text..." />

            <p style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '0.5rem' }}>Answers (check correct ones):</p>
            {question.answers.map((answer, aIndex) => (
              <div key={aIndex} style={styles.answerRow}>
                <input type={question.question_type === 'multiple_choice' ? 'checkbox' : 'radio'} checked={answer.is_correct} onChange={(e) => updateAnswer(qIndex, aIndex, 'is_correct', e.target.checked)} style={styles.checkbox} name={`q-${qIndex}`} />
                <input value={answer.text} onChange={(e) => updateAnswer(qIndex, aIndex, 'text', e.target.value)} style={styles.answerInput} placeholder={`Answer ${aIndex + 1}`} />
                <button style={styles.removeBtn} onClick={() => removeAnswer(qIndex, aIndex)}>
                  <FiTrash2 size={14} />
                </button>
              </div>
            ))}
            <button style={{ ...styles.addBtn, marginTop: '0.5rem' }} onClick={() => addAnswer(qIndex)}>
              <FiPlus size={14} /> Add Answer
            </button>

            <div style={{ marginTop: '0.75rem' }}>
              <input value={question.explanation} onChange={(e) => updateQuestion(qIndex, 'explanation', e.target.value)} style={{ ...styles.input, width: '100%' }} placeholder="Explanation (shown after answering)" />
            </div>
          </div>
        ))}

        <button type="button" style={styles.addBtn} onClick={addQuestion}>
          <FiPlus size={16} /> Add Question
        </button>

        <button style={styles.saveBtn} onClick={handleSave} disabled={saving}>
          <FiSave size={18} /> {saving ? 'Saving...' : 'Save Quiz'}
        </button>
      </div>
    </div>
  );
}
