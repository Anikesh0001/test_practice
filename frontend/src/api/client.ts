/// <reference types="vite/client" />
import axios from "axios";

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://localhost:8000";

export const api = axios.create({
  baseURL: apiBaseUrl
});
