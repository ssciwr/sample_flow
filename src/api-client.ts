import axios from "axios";
import type { AxiosInstance } from "axios";
import { useUserStore } from "@/stores/user";

const apiClient: AxiosInstance = axios.create({
  baseURL: "http://localhost:5000",
  headers: {
    "Content-type": "application/json",
  },
});

apiClient.interceptors.request.use(function (config) {
  const user = useUserStore();
  config.headers.Authorization = `Bearer ${user.token}`;
  return config;
});

export default apiClient;
