import axios from "axios";
import type { AxiosInstance } from "axios";
import { useUserStore } from "@/stores/user";

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_REST_API_LOCATION,
  headers: {
    "Content-type": "application/json",
  },
});

apiClient.interceptors.request.use(function (config) {
  const user = useUserStore();
  config.headers.Authorization = `Bearer ${user.token}`;
  return config;
});

function download_reference_sequence(primary_key: string) {
  apiClient
    .post(
      "reference_sequence",
      {
        primary_key: primary_key,
      },
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        responseType: "blob",
      }
    )
    .then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${primary_key}_reference_sequence.fasta`);
      document.body.appendChild(link);
      link.click();
    });
}
export { apiClient, download_reference_sequence };
