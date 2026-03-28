import api from './axiosConfig';

const quizApi = {
  // Quiz CRUD (instructor)
  getQuiz: (quizId) => api.get(`/quizzes/${quizId}/`),
  createQuiz: (data) => api.post('/quizzes/', data),
  updateQuiz: (quizId, data) => api.patch(`/quizzes/${quizId}/`, data),
  deleteQuiz: (quizId) => api.delete(`/quizzes/${quizId}/`),

  // Questions (instructor)
  getQuestions: (quizId) => api.get(`/quizzes/${quizId}/questions/`),
  createQuestion: (quizId, data) => api.post(`/quizzes/${quizId}/questions/`, data),
  updateQuestion: (quizId, questionId, data) =>
    api.patch(`/quizzes/${quizId}/questions/${questionId}/`, data),
  deleteQuestion: (quizId, questionId) =>
    api.delete(`/quizzes/${quizId}/questions/${questionId}/`),

  // Student quiz flow
  startQuiz: (quizId) => api.post(`/quizzes/${quizId}/start/`),
  submitQuiz: (quizId, attemptId, responses) =>
    api.post(`/quizzes/${quizId}/submit/${attemptId}/`, { responses }),
  getQuizResults: (quizId) => api.get(`/quizzes/${quizId}/results/`),
};

export default quizApi;
