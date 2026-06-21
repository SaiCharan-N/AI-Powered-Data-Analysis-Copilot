import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 120000,
});

export async function uploadCsv(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post("/api/v1/csv/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}

export async function runQuery(question) {
  const response = await apiClient.post("/api/v1/query/run", { question });
  return response.data;
}

export default apiClient;
