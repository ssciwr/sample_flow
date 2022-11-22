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

function download_file_from_endpoint(
  endpoint: string,
  json: object,
  filename: string
) {
  apiClient
    .post(endpoint, json, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      responseType: "blob",
    })
    .then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
    });
}

function download_reference_sequence(primary_key: string) {
  download_file_from_endpoint(
    "reference_sequence",
    { primary_key: primary_key },
    `${primary_key}_reference_sequence.fasta`
  );
}

function download_result(primary_key: string, filetype: string) {
  download_file_from_endpoint(
    "result",
    { primary_key: primary_key, filetype: filetype },
    `${primary_key}.${filetype}`
  );
}

function download_zipsamples() {
  download_file_from_endpoint("admin/zipsamples", {}, "samples.zip");
}

export {
  apiClient,
  download_zipsamples,
  download_reference_sequence,
  download_result,
};
