import { Question } from "../api/types";

type QuestionCardProps = {
  question: Question;
  selectedAnswer: string | null;
  onSelect: (value: string) => void;
  onFreeTextChange: (value: string) => void;
  bookmarked: boolean;
  onBookmark: () => void;
  index: number;
  total: number;
};

const QuestionCard = ({
  question,
  selectedAnswer,
  onSelect,
  onFreeTextChange,
  bookmarked,
  onBookmark,
  index,
  total
}: QuestionCardProps) => {
  const options = question.options || {};
  const optionKeys = Object.keys(options);
  const hasOptions = optionKeys.length > 0;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
          Question {index + 1} of {total}
        </p>
        <button
          onClick={onBookmark}
          className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
            bookmarked
              ? "bg-amber-200 text-amber-900"
              : "border border-slate-200 text-slate-500 hover:border-amber-300 hover:text-amber-700 dark:border-slate-700"
          }`}
        >
          {bookmarked ? "Bookmarked" : "Bookmark"}
        </button>
      </div>

      <h2 className="mt-4 text-lg font-semibold leading-relaxed">{question.text}</h2>

      <div className="mt-6 space-y-3">
        {hasOptions ? (
          optionKeys.map((key) => (
            <label
              key={key}
              className={`flex cursor-pointer items-start gap-3 rounded-xl border px-4 py-3 transition ${
                selectedAnswer === key
                  ? "border-primary bg-primary/10"
                  : "border-slate-200 hover:border-primary/50 dark:border-slate-700"
              }`}
            >
              <input
                type="radio"
                name={`question-${question.id}`}
                value={key}
                checked={selectedAnswer === key}
                onChange={() => onSelect(key)}
                className="mt-1"
              />
              <div>
                <p className="text-sm font-semibold">{key}.</p>
                <p className="text-sm text-slate-600 dark:text-slate-300">{options[key]}</p>
              </div>
            </label>
          ))
        ) : (
          <textarea
            className="h-32 w-full rounded-xl border border-slate-200 bg-transparent p-3 text-sm text-slate-700 shadow-sm outline-none transition focus:border-primary dark:border-slate-700 dark:text-slate-100"
            placeholder="Write your answer here..."
            value={selectedAnswer || ""}
            onChange={(event) => onFreeTextChange(event.target.value)}
          />
        )}
      </div>
    </div>
  );
};

export default QuestionCard;
