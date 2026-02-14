type ExplanationModalProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  content: string;
  loading?: boolean;
};

const ExplanationModal = ({ open, onClose, title, content, loading }: ExplanationModalProps) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-900">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button
            onClick={onClose}
            className="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-500 hover:text-slate-700 dark:border-slate-700"
          >
            Close
          </button>
        </div>
        <div className="mt-4 text-sm text-slate-600 dark:text-slate-300">
          {loading ? (
            <div className="space-y-2">
              <div className="h-3 w-full animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-3 w-11/12 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-3 w-10/12 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
            </div>
          ) : (
            <p className="whitespace-pre-line">{content}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExplanationModal;
