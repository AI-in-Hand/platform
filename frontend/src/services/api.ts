import axios from 'axios';

const API_ENDPOINT = 'http://localhost:5000'; // Your backend endpoint

export const startConversation = async () => {
  return axios.get(`${API_ENDPOINT}/start`);
};

export const sendMessage = async (threadId: string, message: string) => {
  return axios.post(`${API_ENDPOINT}/chat`, { thread_id: threadId, message });
};
