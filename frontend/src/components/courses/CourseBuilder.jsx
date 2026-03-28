import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import { FiPlus, FiTrash2, FiSave, FiUpload } from 'react-icons/fi';
import courseApi from '../../api/courseApi';

const styles = {
  container: { maxWidth: '900px', margin: '0 auto', padding: '2rem' },
  title: { fontSize: '1.8rem', fontWeight: 700, marginBottom: '2rem', color: '#111827' },
  form: { display: 'flex', flexDirection: 'column', gap: '1.5rem' },
  group: { display: 'flex', flexDirection: 'column', gap: '0.4rem' },
  label: { fontSize: '0.9rem', fontWeight: 600, color: '#374151' },
  input: {
    padding: '0.65rem 0.9rem', borderRadius: '6px', border: '1px solid #d1d5db',
    fontSize: '0.95rem', outline: 'none',
  },
  textarea: {
    padding: '0.65rem 0.9rem', borderRadius: '6px', border: '1px solid #d1d5db',
    fontSize: '0.95rem', outline: 'none', minHeight: '120px', resize: 'vertical',
  },
  select: {
    padding: '0.65rem 0.9rem', borderRadius: '6px', border: '1px solid #d1d5db',
    fontSize: '0.95rem', backgroundColor: '#fff',
  },
  row: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' },
  listSection: {
    border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem',
  },
  listItem: {
    display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem',
  },
  listInput: {
    flex: 1, padding: '0.5rem', borderRadius: '4px', border: '1px solid #d1d5db',
    fontSize: '0.9rem',
  },
  addBtn: {
    display: 'flex', alignItems: 'center', gap: '0.3rem',
    padding: '0.4rem 0.8rem', backgroundColor: '#f3f4f6', border: '1px solid #d1d5db',
    borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem',
  },
  removeBtn: {
    backgroundColor: 'transparent', border: 'none', cursor: 'pointer',
    color: '#ef4444', padding: '0.3rem',
  },
  submitBtn: {
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
    padding: '0.75rem 2rem', backgroundColor: '#4f46e5', color: '#fff',
    border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600,
    cursor: 'pointer', alignSelf: 'flex-start',
  },
};

export default function CourseBuilder() {
  const navigate = useNavigate();
  const { categories } = useSelector((state) => state.courses);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: '', subtitle: '', description: '',
    category: '', level: 'all_levels', language: 'en',
    price: '', is_free: false, thumbnail: null,
    requirements: [''], what_you_learn: [''], tags: [''],
  });

  const handleChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    if (type === 'file') {
      setFormData((prev) => ({ ...prev, [name]: files[0] }));
    } else if (type === 'checkbox') {
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleListChange = (field, index, value) => {
    setFormData((prev) => {
      const updated = [...prev[field]];
      updated[index] = value;
      return { ...prev, [field]: updated };
    });
  };

  const addListItem = (field) => {
    setFormData((prev) => ({ ...prev, [field]: [...prev[field], ''] }));
  };

  const removeListItem = (field, index) => {
    setFormData((prev) => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const data = {
        ...formData,
        requirements: formData.requirements.filter(Boolean),
        what_you_learn: formData.what_you_learn.filter(Boolean),
        tags: formData.tags.filter(Boolean),
        price: formData.is_free ? 0 : parseFloat(formData.price) || 0,
      };

      const { data: course } = await courseApi.createCourse(data);
      toast.success('Course created successfully!');
      navigate(`/instructor/courses/${course.slug}/edit`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create course.');
    } finally {
      setSubmitting(false);
    }
  };

  const renderListEditor = (field, label) => (
    <div style={styles.listSection}>
      <p style={styles.label}>{label}</p>
      {formData[field].map((item, index) => (
        <div key={index} style={styles.listItem}>
          <input
            type="text"
            value={item}
            onChange={(e) => handleListChange(field, index, e.target.value)}
            style={styles.listInput}
            placeholder={`Item ${index + 1}`}
          />
          {formData[field].length > 1 && (
            <button style={styles.removeBtn} onClick={() => removeListItem(field, index)}>
              <FiTrash2 size={16} />
            </button>
          )}
        </div>
      ))}
      <button type="button" style={styles.addBtn} onClick={() => addListItem(field)}>
        <FiPlus size={14} /> Add
      </button>
    </div>
  );

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Create New Course</h1>
      <form style={styles.form} onSubmit={handleSubmit}>
        <div style={styles.group}>
          <label style={styles.label}>Course Title</label>
          <input name="title" value={formData.title} onChange={handleChange} style={styles.input} required placeholder="e.g., Complete React Developer Course" />
        </div>

        <div style={styles.group}>
          <label style={styles.label}>Subtitle</label>
          <input name="subtitle" value={formData.subtitle} onChange={handleChange} style={styles.input} placeholder="Brief description shown in search results" />
        </div>

        <div style={styles.group}>
          <label style={styles.label}>Description</label>
          <textarea name="description" value={formData.description} onChange={handleChange} style={styles.textarea} required placeholder="Detailed course description..." />
        </div>

        <div style={styles.row}>
          <div style={styles.group}>
            <label style={styles.label}>Category</label>
            <select name="category" value={formData.category} onChange={handleChange} style={styles.select}>
              <option value="">Select Category</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div style={styles.group}>
            <label style={styles.label}>Level</label>
            <select name="level" value={formData.level} onChange={handleChange} style={styles.select}>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="all_levels">All Levels</option>
            </select>
          </div>
        </div>

        <div style={styles.row}>
          <div style={styles.group}>
            <label style={styles.label}>
              <input type="checkbox" name="is_free" checked={formData.is_free} onChange={handleChange} style={{ marginRight: '0.5rem' }} />
              Free Course
            </label>
          </div>
          {!formData.is_free && (
            <div style={styles.group}>
              <label style={styles.label}>Price (USD)</label>
              <input name="price" type="number" value={formData.price} onChange={handleChange} style={styles.input} min="0" step="0.01" placeholder="29.99" />
            </div>
          )}
        </div>

        <div style={styles.group}>
          <label style={styles.label}>Thumbnail Image</label>
          <input name="thumbnail" type="file" accept="image/*" onChange={handleChange} style={styles.input} />
        </div>

        {renderListEditor('what_you_learn', 'What Students Will Learn')}
        {renderListEditor('requirements', 'Requirements / Prerequisites')}
        {renderListEditor('tags', 'Tags')}

        <button type="submit" style={styles.submitBtn} disabled={submitting}>
          <FiSave size={18} /> {submitting ? 'Creating...' : 'Create Course'}
        </button>
      </form>
    </div>
  );
}
