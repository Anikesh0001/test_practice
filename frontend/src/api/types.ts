export type Question = {
  id: number;
  number: number;
  text: string;
  options?: Record<string, string> | null;
};

export type UploadResponse = {
  test_id: number;
  questions: Question[];
};

export type StartTestResponse = {
  test_id: number;
  duration_minutes: number;
  questions: Question[];
};

export type ResultDetail = {
  question_id: number;
  user_answer: string | null;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
};

export type SubmitResponse = {
  result_id: number;
  test_id: number;
  score: number;
  accuracy: number;
  correct_count: number;
  wrong_count: number;
  details: ResultDetail[];
};

export type ExplanationResponse = {
  question_id: number;
  explanation: string;
};

export type RetryResponse = {
  test_id: number;
  questions: Question[];
};
