import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api/axiosConfig';

export const fetchCourseProgress = createAsyncThunk(
  'progress/fetchCourseProgress',
  async (courseSlug, { rejectWithValue }) => {
    try {
      const { data } = await api.get(`/progress/courses/${courseSlug}/`);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const fetchLessonProgress = createAsyncThunk(
  'progress/fetchLessonProgress',
  async (courseSlug, { rejectWithValue }) => {
    try {
      const { data } = await api.get(`/progress/courses/${courseSlug}/lessons/`);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const updateLessonProgress = createAsyncThunk(
  'progress/updateLessonProgress',
  async ({ lessonId, progressData }, { rejectWithValue }) => {
    try {
      const { data } = await api.post(`/progress/lessons/${lessonId}/update/`, progressData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const markLessonComplete = createAsyncThunk(
  'progress/markLessonComplete',
  async (lessonId, { rejectWithValue }) => {
    try {
      const { data } = await api.post(`/progress/lessons/${lessonId}/complete/`);
      return { lessonId, ...data };
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const fetchAchievements = createAsyncThunk(
  'progress/fetchAchievements',
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await api.get('/progress/achievements/');
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

const progressSlice = createSlice({
  name: 'progress',
  initialState: {
    courseProgress: null,
    lessonProgress: {},
    achievements: [],
    loading: false,
    error: null,
  },
  reducers: {
    setCurrentLessonProgress: (state, action) => {
      const { lessonId, data } = action.payload;
      state.lessonProgress[lessonId] = data;
    },
    clearProgress: (state) => {
      state.courseProgress = null;
      state.lessonProgress = {};
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCourseProgress.pending, (state) => { state.loading = true; })
      .addCase(fetchCourseProgress.fulfilled, (state, action) => {
        state.loading = false;
        state.courseProgress = action.payload;
      })
      .addCase(fetchCourseProgress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchLessonProgress.fulfilled, (state, action) => {
        const lessons = action.payload.results || action.payload;
        lessons.forEach((lp) => {
          state.lessonProgress[lp.lesson] = lp;
        });
      })
      .addCase(updateLessonProgress.fulfilled, (state, action) => {
        const lessonId = action.payload.lesson;
        state.lessonProgress[lessonId] = action.payload;
      })
      .addCase(markLessonComplete.fulfilled, (state, action) => {
        const { lessonId, course_progress } = action.payload;
        if (state.lessonProgress[lessonId]) {
          state.lessonProgress[lessonId].status = 'completed';
        }
        if (state.courseProgress && course_progress !== undefined) {
          state.courseProgress.progress_percent = course_progress;
        }
      })
      .addCase(fetchAchievements.fulfilled, (state, action) => {
        state.achievements = action.payload.results || action.payload;
      });
  },
});

export const { setCurrentLessonProgress, clearProgress } = progressSlice.actions;
export default progressSlice.reducer;
