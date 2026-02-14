import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import Timer from "../components/Timer";
import QuestionCard from "../components/QuestionCard";
import { startTest, submitTest } from "../api";
import { Question, StartTestResponse } from "../api/types";

type StoredTest = {
  test_id: number;
  questions: Question[];
};

type PersistedState = {
  answers: Record<number, string | null>;
  bookmarks: number[];
  currentIndex: number;
  durationMinutes: number;
  started: boolean;
  remainingSeconds?: number;
};

const Test = () => {
  const navigate = useNavigate();
  const storedTest = localStorage.getItem("currentTest");
  const parsedTest = useMemo(
    () => (storedTest ? (JSON.parse(storedTest) as StoredTest) : null),
    [storedTest]
  );

  const [questions, setQuestions] = useState<Question[]>(parsedTest?.questions || []);
  const [durationMinutes, setDurationMinutes] = useState(30);
  const [started, setStarted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string | null>>({});
  const [bookmarks, setBookmarks] = useState<Set<number>>(new Set());
  const [saving, setSaving] = useState(false);
  const [timerSeed, setTimerSeed] = useState(durationMinutes * 60);
  const [remainingSeconds, setRemainingSeconds] = useState(durationMinutes * 60);
  const [timerVersion, setTimerVersion] = useState(0);

  const storageKey = parsedTest ? `testState-${parsedTest.test_id}` : "testState";

  useEffect(() => {
    if (!parsedTest) return;
    const persisted = localStorage.getItem(storageKey);
    if (persisted) {
      const data: PersistedState = JSON.parse(persisted);
      setAnswers(data.answers || {});
      setBookmarks(new Set(data.bookmarks || []));
      setCurrentIndex(data.currentIndex || 0);
      setDurationMinutes(data.durationMinutes || 30);
      setStarted(data.started || false);
      const remaining = data.remainingSeconds ?? (data.durationMinutes || 30) * 60;
      setTimerSeed(remaining);
      setRemainingSeconds(remaining);
      if (data.started) {
        setTimerVersion((prev) => prev + 1);
      }
    }
  }, [parsedTest, storageKey]);

  useEffect(() => {
    if (!parsedTest) return;
    const data: PersistedState = {
      answers,
      bookmarks: Array.from(bookmarks),
      currentIndex,
      durationMinutes,
      started,
      remainingSeconds
    };
    localStorage.setItem(storageKey, JSON.stringify(data));
  }, [answers, bookmarks, currentIndex, durationMinutes, started, remainingSeconds, parsedTest, storageKey]);

  const answeredCount = useMemo(
    () =>
      Object.values(answers).filter(
        (value) => typeof value === "string" && value.trim() !== ""
      ).length,
    [answers]
  );

  const handleStart = async () => {
    if (!parsedTest) return;
    try {
      const response: StartTestResponse = await startTest(parsedTest.test_id, durationMinutes);
      const nextQuestions = response.questions?.length
        ? response.questions
        : parsedTest.questions || [];
      if (!nextQuestions.length) {
        toast.error("No questions available to start the test.");
        return;
      }
      setQuestions(nextQuestions);
      setCurrentIndex(0);
      setStarted(true);
      localStorage.setItem(
        "currentTest",
        JSON.stringify({ test_id: response.test_id, questions: nextQuestions })
      );
      const seed = durationMinutes * 60;
      setTimerSeed(seed);
      setRemainingSeconds(seed);
      setTimerVersion((prev) => prev + 1);
      toast.success("Test started. Good luck!");
    } catch (error) {
      toast.error("Unable to start the test.");
    }
  };

  const handleSubmit = async () => {
    if (!parsedTest) return;
    if (saving) return;
    try {
      setSaving(true);
      const response = await submitTest(parsedTest.test_id, answers);
      localStorage.setItem("latestResult", JSON.stringify(response));
      toast.success("Test submitted successfully.");
      navigate("/result");
    } catch (error) {
      toast.error("Submission failed. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleExpire = () => {
    toast("Time is up. Submitting your test.");
    handleSubmit();
  };

  const handleBookmark = (questionId: number) => {
    setBookmarks((prev: Set<number>) => {
      const updated = new Set(prev);
      if (updated.has(questionId)) {
        updated.delete(questionId);
      } else {
        updated.add(questionId);
      }
      return updated;
    });
  };

  const toggleFullscreen = async () => {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen();
    } else {
      await document.exitFullscreen();
    }
  };

  const currentQuestion = questions[currentIndex];

  useEffect(() => {
    if (!questions.length) return;
    setCurrentIndex((prev) => Math.min(Math.max(prev, 0), questions.length - 1));
  }, [questions]);

  useEffect(() => {
    if (!started) return;
    if (questions.length > 0) return;
    if (parsedTest?.questions?.length) {
      setQuestions(parsedTest.questions);
      setCurrentIndex(0);
    }
  }, [started, questions.length, parsedTest?.questions]);

  if (!parsedTest) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">No active test found.</h2>
        <p className="mt-2 text-sm text-slate-500">Please upload a PDF to begin.</p>
      </div>
    );
  }

  if (!started) {
    return (
      <div className="fade-in grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-xl font-semibold">Ready to begin?</h2>
          <p className="mt-2 text-sm text-slate-500">
            Select your duration, shuffle questions, and start the test.
          </p>
          <div className="mt-5">
            <label className="text-sm font-medium text-slate-600 dark:text-slate-300">
              Test duration (minutes)
            </label>
            <select
              value={durationMinutes}
              onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                setDurationMinutes(Number(event.target.value))
              }
              className="mt-2 w-full rounded-xl border border-slate-200 bg-transparent px-4 py-2 text-sm dark:border-slate-700"
            >
              {[15, 30, 45, 60, 90].map((minutes) => (
                <option key={minutes} value={minutes}>
                  {minutes} minutes
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={handleStart}
            className="mt-6 w-full rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow transition hover:opacity-90"
          >
            Start Test
          </button>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-lg font-semibold">Test Summary</h3>
          <div className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-300">
            <p>Total questions: {questions.length}</p>
            <p>Shuffle: enabled</p>
            <p>Auto-submit: on timer end</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in grid gap-6 lg:grid-cols-[1fr_320px]">
      <div className="space-y-6">
        <Timer
          initialSeconds={timerSeed}
          resetKey={timerVersion}
          onExpire={handleExpire}
          onTick={setRemainingSeconds}
        />
        {currentQuestion && (
          <QuestionCard
            question={currentQuestion}
            selectedAnswer={answers[currentQuestion.id] || null}
            onSelect={(value) =>
              setAnswers((prev) => ({
                ...prev,
                [currentQuestion.id]: value
              }))
            }
            onFreeTextChange={(value) =>
              setAnswers((prev) => ({
                ...prev,
                [currentQuestion.id]: value
              }))
            }
            bookmarked={bookmarks.has(currentQuestion.id)}
            onBookmark={() => handleBookmark(currentQuestion.id)}
            index={currentIndex}
            total={questions.length}
          />
        )}

        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:border-primary hover:text-primary dark:border-slate-700"
          >
            Previous
          </button>
          <button
            onClick={() =>
              setCurrentIndex((prev) => Math.min(questions.length - 1, prev + 1))
            }
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:border-primary hover:text-primary dark:border-slate-700"
          >
            Next
          </button>
          <button
            onClick={() => {
              const firstUnanswered = questions.findIndex(
                (question) => !answers[question.id]
              );
              if (firstUnanswered !== -1) {
                setCurrentIndex(firstUnanswered);
              }
            }}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:border-primary hover:text-primary dark:border-slate-700"
          >
            Review Unanswered
          </button>
          <button
            onClick={toggleFullscreen}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:border-primary hover:text-primary dark:border-slate-700"
          >
            Toggle Fullscreen
          </button>
        </div>
      </div>

      <aside className="space-y-6">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-300">
            Progress
          </h3>
          <div className="mt-3 text-2xl font-semibold">
            {answeredCount}/{questions.length}
          </div>
          <div className="mt-3 h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800">
            <div
              className="h-2 rounded-full bg-primary transition-all"
              style={{ width: `${(answeredCount / questions.length) * 100}%` }}
            />
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-300">
            Question Navigator
          </h3>
          <div className="mt-4 grid grid-cols-5 gap-2">
            {questions.map((question, index) => {
              const answered = Boolean(answers[question.id]);
              const bookmarked = bookmarks.has(question.id);
              return (
                <button
                  key={question.id}
                  onClick={() => setCurrentIndex(index)}
                  className={`rounded-lg border px-2 py-1 text-xs font-semibold transition ${
                    index === currentIndex
                      ? "border-primary bg-primary/10 text-primary"
                      : answered
                      ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                      : "border-slate-200 text-slate-500 dark:border-slate-700"
                  }`}
                >
                  {index + 1}
                  {bookmarked ? "★" : ""}
                </button>
              );
            })}
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={saving}
          className="w-full rounded-2xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow transition hover:opacity-90 disabled:opacity-60"
        >
          {saving ? "Submitting..." : "Submit Test"}
        </button>
      </aside>
    </div>
  );
};

export default Test;
