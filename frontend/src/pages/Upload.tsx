import { useCallback, useState, type DragEvent, type ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { uploadPdf, generateCompanyTest } from "../api";
import { UploadResponse } from "../api/types";

const Upload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"pdf" | "company">("pdf");
  const [companyName, setCompanyName] = useState("");
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

  const handleCompanyTest = async () => {
    if (!companyName.trim()) {
      toast.error("Please enter a company name.");
      return;
    }

    try {
      setLoading(true);
      const response = await generateCompanyTest(companyName.trim());
      
      // Fetch the test to get questions (reuse existing start test endpoint)
      const testData = {
        test_id: response.test_id,
        questions: [] // Will be fetched when test starts
      };
      
      localStorage.setItem("currentTest", JSON.stringify(testData));
      toast.success(response.message);
      navigate("/test");
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "Failed to generate company test.";
      toast.error(errorMsg);
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
          <h1 className="text-3xl font-semibold">AI-Powered Test Generator</h1>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Upload a PDF or generate a company-based assessment with AI.
          </p>

          {/* Mode Toggle */}
          <div className="mt-6 flex gap-3">
            <button
              onClick={() => setMode("pdf")}
              className={`flex-1 rounded-xl border-2 px-4 py-3 text-sm font-semibold transition ${
                mode === "pdf"
                  ? "border-primary bg-primary/5 text-primary"
                  : "border-slate-200 text-slate-600 dark:border-slate-700 dark:text-slate-300"
              }`}
            >
              📄 Upload PDF
            </button>
            <button
              onClick={() => setMode("company")}
              className={`flex-1 rounded-xl border-2 px-4 py-3 text-sm font-semibold transition ${
                mode === "company"
                  ? "border-primary bg-primary/5 text-primary"
                  : "border-slate-200 text-slate-600 dark:border-slate-700 dark:text-slate-300"
              }`}
            >
              🏢 Generate by Company
            </button>
          </div>

          {/* PDF Upload Mode */}
          {mode === "pdf" && (
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
          )}

          {/* Company Mode */}
          {mode === "company" && (
            <div className="mt-6 rounded-3xl border-2 border-slate-200 bg-white p-8 dark:border-slate-700 dark:bg-slate-900">
              <h3 className="text-lg font-semibold">Generate Company Assessment</h3>
              <p className="mt-2 text-sm text-slate-500">
                Enter a company name to generate a realistic assessment based on their hiring pattern.
              </p>
              
              <div className="mt-4">
                <label className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  Company Name
                </label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setCompanyName(e.target.value)}
                  placeholder="e.g., Google, Amazon, Microsoft"
                  className="mt-2 w-full rounded-xl border border-slate-200 bg-transparent px-4 py-3 text-sm dark:border-slate-700"
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      handleCompanyTest();
                    }
                  }}
                />
              </div>

              <button
                onClick={handleCompanyTest}
                disabled={loading || !companyName.trim()}
                className="mt-6 w-full rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow transition hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Generating Assessment..." : "Generate Test"}
              </button>

              <p className="mt-3 text-xs text-slate-500">
                💡 The AI will research the company's hiring pattern and generate a realistic assessment.
              </p>
            </div>
          )}

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
            <li>• <strong>PDF Mode:</strong> Upload assessment PDF with MCQs.</li>
            <li>• <strong>Company Mode:</strong> AI researches hiring patterns.</li>
            <li>• Select duration and start the test.</li>
            <li>• AI evaluates answers and explains them.</li>
            <li>• Download a PDF report when finished.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Upload;
