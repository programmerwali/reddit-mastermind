import axios from 'axios';

const API_BASE_URL = 'https://reddit-mastermind-backend-bb3y.onrender.com';

export const api = {
  async generateCalendar(data) {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/generate-calendar`, data);
      return response.data;
    } catch (error) {
      console.error('Error generating calendar:', error);
      throw error;
    }
  },

  async generateNextWeek(data) {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/generate-next-week`, data);
      return response.data;
    } catch (error) {
      console.error('Error generating next week:', error);
      throw error;
    }
  },

  async healthCheck() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};
