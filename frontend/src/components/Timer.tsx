import { useEffect, useState } from "react";

type TimerProps = {
  initialSeconds: number;
  resetKey: number;
  onExpire: () => void;
  onTick?: (remaining: number) => void;
};

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
};

const Timer = ({ initialSeconds, resetKey, onExpire, onTick }: TimerProps) => {
  const [remaining, setRemaining] = useState(initialSeconds);

  useEffect(() => {
    setRemaining(initialSeconds);
  }, [initialSeconds, resetKey]);

  useEffect(() => {
    if (remaining <= 0) {
      onExpire();
      return;
    }

    const timer = setInterval(() => {
      setRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(timer);
  }, [remaining, onExpire]);

  useEffect(() => {
    onTick?.(remaining);
  }, [remaining, onTick]);

  const progress = Math.max(0, (remaining / initialSeconds) * 100);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
          Time remaining
        </span>
        <span className="text-lg font-semibold">{formatTime(remaining)}</span>
      </div>
      <div className="mt-3 h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className="h-2 rounded-full bg-primary transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

export default Timer;
