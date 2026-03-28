import api from './axiosConfig';

const courseApi = {
  // Categories
  getCategories: () => api.get('/courses/categories/'),

  // Courses - public
  getCourses: (params = {}) => api.get('/courses/', { params }),
  getCourseBySlug: (slug) => api.get(`/courses/${slug}/`),
  searchCourses: (query) => api.get('/courses/', { params: { search: query } }),

  // Courses - instructor
  getInstructorCourses: () => api.get('/courses/instructor-courses/'),
  createCourse: (data) => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        if (Array.isArray(value)) {
          formData.append(key, JSON.stringify(value));
        } else {
          formData.append(key, value);
        }
      }
    });
    return api.post('/courses/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  updateCourse: (slug, data) => api.patch(`/courses/${slug}/`, data),
  publishCourse: (slug) => api.post(`/courses/${slug}/publish/`),

  // Sections
  getCourseSections: (courseSlug) => api.get(`/courses/${courseSlug}/sections/`),
  createSection: (courseSlug, data) => api.post(`/courses/${courseSlug}/sections/`, data),
  updateSection: (courseSlug, sectionId, data) =>
    api.patch(`/courses/${courseSlug}/sections/${sectionId}/`, data),
  deleteSection: (courseSlug, sectionId) =>
    api.delete(`/courses/${courseSlug}/sections/${sectionId}/`),

  // Enrollments
  enrollInCourse: (slug) => api.post(`/courses/${slug}/enroll/`),
  getMyCourses: () => api.get('/courses/my_courses/'),

  // Reviews
  getCourseReviews: (courseSlug) => api.get(`/courses/${courseSlug}/reviews/`),
  createReview: (courseSlug, data) => api.post(`/courses/${courseSlug}/reviews/`, data),
  markReviewHelpful: (courseSlug, reviewId) =>
    api.post(`/courses/${courseSlug}/reviews/${reviewId}/helpful/`),
};

export default courseApi;
