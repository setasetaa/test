import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
});

export const uploadReceipt = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getExpenses = (params) => api.get('/api/expenses', { params });
export const updateExpense = (id, data) => api.put(`/api/expenses/${id}`, data);
export const deleteExpense = (id) => api.delete(`/api/expenses/${id}`);
export const getSummary = (month) => api.get('/api/summary', { params: month ? { month } : {} });

export default api;
