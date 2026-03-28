import api from './axiosConfig';

const paymentApi = {
  // Checkout
  createCheckout: (courseId, couponCode = '') =>
    api.post('/payments/checkout/', {
      course_id: courseId,
      coupon_code: couponCode,
    }),

  // Payment history
  getPaymentHistory: () => api.get('/payments/history/'),

  // Coupons
  validateCoupon: (code, courseId) =>
    api.post('/payments/coupons/validate/', { code, course_id: courseId }),
  getCoupons: () => api.get('/payments/coupons/'),
  createCoupon: (data) => api.post('/payments/coupons/', data),
  deleteCoupon: (couponId) => api.delete(`/payments/coupons/${couponId}/`),

  // Refunds
  requestRefund: (paymentId, amount, reason) =>
    api.post('/payments/refunds/', {
      payment: paymentId,
      amount,
      reason,
    }),

  // Instructor payouts
  getPayouts: () => api.get('/payments/payouts/'),
};

export default paymentApi;
