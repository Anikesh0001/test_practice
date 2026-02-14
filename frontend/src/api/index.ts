import { api } from "./client";
import {
  ExplanationResponse,
  RetryResponse,
  StartTestResponse,
  SubmitResponse,
  UploadResponse
} from "./types";

export const uploadPdf = async (file: File): Promise<UploadResponse> => {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<UploadResponse>("/api/upload", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
};

export const startTest = async (
  testId: number,
  durationMinutes: number
): Promise<StartTestResponse> => {
  const { data } = await api.post<StartTestResponse>(`/api/tests/${testId}/start`, {
    duration_minutes: durationMinutes
  });
  return data;
};

export const submitTest = async (
  testId: number,
  answers: Record<number, string | null>
): Promise<SubmitResponse> => {
  const { data } = await api.post<SubmitResponse>(`/api/tests/${testId}/submit`, {
    answers
  });
  return data;
};

export const retryTest = async (testId: number): Promise<RetryResponse> => {
  const { data } = await api.post<RetryResponse>(`/api/tests/${testId}/retry`);
  return data;
};

export const explainAnswer = async (
  questionId: number,
  correctAnswer: string
): Promise<ExplanationResponse> => {
  const { data } = await api.post<ExplanationResponse>("/api/explanations", {
    question_id: questionId,
    correct_answer: correctAnswer
  });
  return data;
};
