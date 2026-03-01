import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
});

// Helper to normalize errors
const handleApiError = (error, context) => {
    console.error(`API Error (${context}):`, error);
    if (error.response) {
        // Server responded with a status code outside 2xx
        const message = error.response.data?.detail || error.response.data?.message || "Server error";
        throw new Error(message);
    } else if (error.request) {
        // Request was made but no response received
        throw new Error("Cannot connect to server. Is the backend running?");
    } else {
        // Request setup error
        throw new Error(error.message);
    }
};

export const uploadFiles = async (files) => {
    try {
        const formData = new FormData();
        Array.from(files).forEach((file) => {
            formData.append('files', file);
        });
        const response = await api.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            timeout: 30000, // 30s upload timeout
        });
        return response.data;
    } catch (error) {
        handleApiError(error, "uploadFiles");
    }
};

export const askQuestion = async (question) => {
    try {
        const response = await axios.post(`${API_URL}/ask`, { question }, { timeout: 60000 }); // 60s timeout for LLM
        return response.data;
    } catch (error) {
        handleApiError(error, "askQuestion");
    }
};

export const getHealth = async () => {
    try {
        const response = await api.get('/health', { timeout: 5000 });
        return response.data;
    } catch (error) {
        return { status: "offline", error: error.message };
    }
};

export const getSuggestedQuestions = async () => {
    try {
        const response = await api.get('/suggested-questions', { timeout: 10000 });
        return response.data;
    } catch (error) {
        console.warn("Failed to fetch suggestions:", error);
        return { questions: [] }; // Fail silently for suggestions
    }
};
