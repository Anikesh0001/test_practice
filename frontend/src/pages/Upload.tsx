import { useCallback, useState, type DragEvent } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { uploadPdf } from "../api";
import { UploadResponse } from "../api/types";

const Upload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (file: File) => {
    try {
      setLoading(true);
      const data: UploadResponse = await uploadPdf(file);
      localStorage.setItem("currentTest", JSON.stringify(data));
      toast.success("PDF processed successfully.");
      navigate("/test");
    } catch (error) {
      toast.error("Unable to process PDF. Please try another file.");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setDragActive(false);
      const file = event.dataTransfer.files?.[0];
      if (file) {
        handleUpload(file);
      }
    },
    []
  );

  return (
    <div className="fade-in">
      <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <div>
          <h1 className="text-3xl font-semibold">PDF-Based Online Test Generator</h1>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Upload your assessment PDF to instantly create a timed test with automatic evaluation.
          </p>

          <div
            onDragOver={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            className={`mt-6 flex h-64 flex-col items-center justify-center rounded-3xl border-2 border-dashed p-6 text-center transition ${
              dragActive
                ? "border-primary bg-primary/5"
                : "border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900"
            }`}
          >
            <p className="text-sm font-semibold">Drag & drop a PDF here</p>
            <p className="mt-2 text-xs text-slate-500">Or click to browse from your device</p>
            <label className="mt-4 cursor-pointer rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white shadow">
              Browse PDF
              <input
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) handleUpload(file);
                }}
              />
            </label>
          </div>

          {loading && (
            <div className="mt-6 space-y-3">
              <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-4 w-2/3 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-4 w-1/2 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
            </div>
          )}
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-semibold">How it works</h2>
          <ul className="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
            <li>• Upload an assessment PDF with MCQs.</li>
            <li>• Select duration and start the test.</li>
            <li>• Gemini evaluates answers and explains them.</li>
            <li>• Download a PDF report when finished.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Upload;
