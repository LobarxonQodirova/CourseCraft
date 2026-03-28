import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import courseApi from '../../api/courseApi';

export const fetchCourses = createAsyncThunk(
  'courses/fetchCourses',
  async (params = {}, { rejectWithValue }) => {
    try {
      const { data } = await courseApi.getCourses(params);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { detail: 'Failed to load courses.' });
    }
  }
);

export const fetchCourseDetail = createAsyncThunk(
  'courses/fetchCourseDetail',
  async (slug, { rejectWithValue }) => {
    try {
      const { data } = await courseApi.getCourseBySlug(slug);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { detail: 'Course not found.' });
    }
  }
);

export const fetchCategories = createAsyncThunk(
  'courses/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await courseApi.getCategories();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const fetchMyCourses = createAsyncThunk(
  'courses/fetchMyCourses',
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await courseApi.getMyCourses();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const enrollInCourse = createAsyncThunk(
  'courses/enroll',
  async (slug, { rejectWithValue }) => {
    try {
      const { data } = await courseApi.enrollInCourse(slug);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

const courseSlice = createSlice({
  name: 'courses',
  initialState: {
    list: [],
    currentCourse: null,
    categories: [],
    myCourses: [],
    loading: false,
    error: null,
    pagination: { count: 0, next: null, previous: null },
    filters: {
      category: '',
      level: '',
      is_free: '',
      search: '',
      ordering: '-created_at',
    },
    cart: JSON.parse(localStorage.getItem('cart') || '[]'),
  },
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = { category: '', level: '', is_free: '', search: '', ordering: '-created_at' };
    },
    addToCart: (state, action) => {
      const course = action.payload;
      if (!state.cart.find((c) => c.id === course.id)) {
        state.cart.push(course);
        localStorage.setItem('cart', JSON.stringify(state.cart));
      }
    },
    removeFromCart: (state, action) => {
      state.cart = state.cart.filter((c) => c.id !== action.payload);
      localStorage.setItem('cart', JSON.stringify(state.cart));
    },
    clearCart: (state) => {
      state.cart = [];
      localStorage.removeItem('cart');
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCourses.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchCourses.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload.results || action.payload;
        if (action.payload.count !== undefined) {
          state.pagination = {
            count: action.payload.count,
            next: action.payload.next,
            previous: action.payload.previous,
          };
        }
      })
      .addCase(fetchCourses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchCourseDetail.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchCourseDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCourse = action.payload;
      })
      .addCase(fetchCourseDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload.results || action.payload;
      })
      .addCase(fetchMyCourses.fulfilled, (state, action) => {
        state.myCourses = action.payload.results || action.payload;
      })
      .addCase(enrollInCourse.fulfilled, (state, action) => {
        if (state.currentCourse) {
          state.currentCourse.is_enrolled = true;
        }
      });
  },
});

export const { setFilters, clearFilters, addToCart, removeFromCart, clearCart } = courseSlice.actions;
export default courseSlice.reducer;
