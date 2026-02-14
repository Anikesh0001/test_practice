import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { jsPDF } from "jspdf";
import ExplanationModal from "../components/ExplanationModal";
import { explainAnswer, retryTest } from "../api";
import { Question, SubmitResponse } from "../api/types";

const Result = () => {
  const navigate = useNavigate();
  const storedResult = localStorage.getItem("latestResult");
  const storedTest = localStorage.getItem("currentTest");
  const result = storedResult ? (JSON.parse(storedResult) as SubmitResponse) : null;
  const test = storedTest ? (JSON.parse(storedTest) as { questions: Question[] }) : null;

  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState("");
  const [modalTitle, setModalTitle] = useState("");
  const [modalLoading, setModalLoading] = useState(false);

  const chartData = useMemo(
    () => [
      { name: "Correct", value: result?.correct_count || 0, fill: "#10b981" },
      { name: "Wrong", value: result?.wrong_count || 0, fill: "#ef4444" }
    ],
    [result]
  );

  const handleExplain = async (questionId: number, correctAnswer: string) => {
    try {
      setModalOpen(true);
      setModalLoading(true);
      setModalTitle("AI Explanation");
      const response = await explainAnswer(questionId, correctAnswer);
      setModalContent(response.explanation);
    } catch (error) {
      setModalContent("Unable to generate explanation right now.");
    } finally {
      setModalLoading(false);
    }
  };

  const handleRetry = async () => {
    if (!result) return;
    try {
      const response = await retryTest(result.test_id);
      localStorage.setItem("currentTest", JSON.stringify(response));
      localStorage.removeItem("latestResult");
      toast.success("New test created.");
      navigate("/test");
    } catch (error) {
      toast.error("Unable to retry test.");
    }
  };

  const downloadPdf = () => {
    if (!result) return;
    const doc = new jsPDF();
    doc.text("Test Results", 14, 20);
    doc.text(`Score: ${result.score}`, 14, 30);
    doc.text(`Accuracy: ${result.accuracy.toFixed(2)}%`, 14, 38);
    doc.text(`Correct: ${result.correct_count}  Wrong: ${result.wrong_count}`, 14, 46);
    let y = 58;
    result.details.forEach((detail, index) => {
      doc.text(`Q${index + 1}: ${detail.correct_answer} (You: ${detail.user_answer || ""})`, 14, y);
      y += 8;
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
    });
    doc.save("test-results.pdf");
  };

  if (!result) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">No results available.</h2>
        <p className="mt-2 text-sm text-slate-500">Complete a test to see results.</p>
      </div>
    );
  }

  return (
    <div className="fade-in space-y-6">
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-xl font-semibold">Your Results</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800">
              <p className="text-sm text-slate-500">Score</p>
              <p className="text-2xl font-semibold">{result.score}</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800">
              <p className="text-sm text-slate-500">Accuracy</p>
              <p className="text-2xl font-semibold">{result.accuracy.toFixed(2)}%</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800">
              <p className="text-sm text-slate-500">Correct</p>
              <p className="text-2xl font-semibold text-emerald-600">
                {result.correct_count}
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800">
              <p className="text-sm text-slate-500">Wrong</p>
              <p className="text-2xl font-semibold text-rose-500">{result.wrong_count}</p>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={handleRetry}
              className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:border-primary hover:text-primary dark:border-slate-700"
            >
              Retry Test
            </button>
            <button
              onClick={downloadPdf}
              className="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white shadow"
            >
              Download PDF
            </button>
            <button
              onClick={() => navigate("/review")}
              className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:border-primary hover:text-primary dark:border-slate-700"
            >
              Full Review
            </button>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-lg font-semibold">Performance Analytics</h3>
          <div className="mt-6 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={50} />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h3 className="text-lg font-semibold">Question Review</h3>
        <div className="mt-4 space-y-4">
          {result.details.map((detail, index) => {
            const question = test?.questions.find((item) => item.id === detail.question_id);
            return (
              <div key={detail.question_id} className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold">Question {index + 1}</p>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-semibold ${
                      detail.is_correct ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-600"
                    }`}
                  >
                    {detail.is_correct ? "Correct" : "Wrong"}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                  {question?.text}
                </p>
                <div className="mt-3 text-xs text-slate-500">
                  Your answer: {detail.user_answer || "-"} | Correct answer: {detail.correct_answer}
                </div>
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
      </div>

      <ExplanationModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={modalTitle}
        content={modalContent}
        loading={modalLoading}
      />
    </div>
  );
};

export default Result;
