import { useMemo, useState } from "react";
import ExplanationModal from "../components/ExplanationModal";
import { explainAnswer } from "../api";
import { Question, SubmitResponse } from "../api/types";

const Review = () => {
  const storedResult = localStorage.getItem("latestResult");
  const storedTest = localStorage.getItem("currentTest");
  const result = storedResult ? (JSON.parse(storedResult) as SubmitResponse) : null;
  const test = storedTest ? (JSON.parse(storedTest) as { test_id?: number; questions: Question[] }) : null;
  const persisted = test?.test_id ? localStorage.getItem(`testState-${test.test_id}`) : null;
  const bookmarks = persisted ? (JSON.parse(persisted).bookmarks as number[]) : [];

  const [filter, setFilter] = useState<"all" | "incorrect" | "bookmarked">("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState("");
  const [modalLoading, setModalLoading] = useState(false);

  const filteredDetails = useMemo<SubmitResponse["details"]>(() => {
    if (!result) return [];
    if (filter === "incorrect") {
      return result.details.filter((detail) => !detail.is_correct);
    }
    if (filter === "bookmarked") {
      return result.details.filter((detail) => bookmarks.includes(detail.question_id));
    }
    return result.details;
  }, [filter, result, bookmarks]);

  const handleExplain = async (questionId: number, correctAnswer: string) => {
    try {
      setModalOpen(true);
      setModalLoading(true);
      const response = await explainAnswer(questionId, correctAnswer);
      setModalContent(response.explanation);
    } catch (error) {
      setModalContent("Unable to generate explanation right now.");
    } finally {
      setModalLoading(false);
    }
  };

  if (!result) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">No review data available.</h2>
        <p className="mt-2 text-sm text-slate-500">Complete a test to review answers.</p>
      </div>
    );
  }

  return (
    <div className="fade-in space-y-6">
      <div className="flex flex-wrap gap-3">
        {(["all", "incorrect", "bookmarked"] as const).map((value) => (
          <button
            key={value}
            onClick={() => setFilter(value)}
            className={`rounded-full px-4 py-2 text-xs font-semibold transition ${
              filter === value
                ? "bg-primary text-white"
                : "border border-slate-200 text-slate-600 dark:border-slate-700"
            }`}
          >
            {value.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {filteredDetails.map((detail, index) => {
          const question = test?.questions.find((item) => item.id === detail.question_id);
          return (
            <div
              key={detail.question_id}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Question {index + 1}</h3>
                <span
                  className={`rounded-full px-2 py-1 text-xs font-semibold ${
                    detail.is_correct ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-600"
                  }`}
                >
                  {detail.is_correct ? "Correct" : "Wrong"}
                </span>
              </div>
              <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{question?.text}</p>
              <p className="mt-2 text-xs text-slate-500">
                Your answer: {detail.user_answer || "-"} | Correct: {detail.correct_answer}
              </p>
              <button
                onClick={() => handleExplain(detail.question_id, detail.correct_answer)}
                className="mt-3 rounded-lg border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-600 hover:border-primary hover:text-primary dark:border-slate-700"
              >
                Explain Answer
              </button>
            </div>
          );
        })}
      </div>

      <ExplanationModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="AI Explanation"
        content={modalContent}
        loading={modalLoading}
      />
    </div>
  );
};

export default Review;
