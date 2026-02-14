import { useEffect, useState } from "react";
import { Link, Route, Routes } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Upload from "./pages/Upload";
import Test from "./pages/Test";
import Result from "./pages/Result";
import Review from "./pages/Review";

const getInitialTheme = () => {
  const saved = localStorage.getItem("theme");
  if (saved === "dark" || saved === "light") {
    return saved;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
};

const App = () => {
  const [theme, setTheme] = useState<"light" | "dark">(getInitialTheme());

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200/60 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/70">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link to="/" className="text-lg font-semibold tracking-tight">
            PDF Test Generator
          </Link>
          <div className="flex items-center gap-3">
            <Link
              to="/review"
              className="rounded-full border border-slate-200 px-3 py-1 text-sm font-medium transition hover:border-primary hover:text-primary dark:border-slate-700"
            >
              Review
            </Link>
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="rounded-full border border-slate-200 px-3 py-1 text-sm font-medium transition hover:border-primary hover:text-primary dark:border-slate-700"
            >
              {theme === "dark" ? "Light" : "Dark"} mode
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Upload />} />
          <Route path="/test" element={<Test />} />
          <Route path="/result" element={<Result />} />
          <Route path="/review" element={<Review />} />
        </Routes>
      </main>

      <Toaster position="top-right" />
    </div>
  );
};

export default App;
