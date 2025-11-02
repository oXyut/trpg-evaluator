'use client';

import { useState } from "react";

export function RunSessionPanel() {
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState(
    [
      { turn: 0, actor: "Keeper", content: "Briefs investigators on ominous cargo." },
      { turn: 1, actor: "pc_alpha", content: "Inspects manifest and rolls Library Use (65)." }
    ] as { turn: number; actor: string; content: string }[]
  );

  const handleRun = () => {
    setIsRunning(true);
    setTimeout(() => {
      setLogs((prev) => [
        ...prev,
        { turn: prev.length, actor: "Keeper", content: "Reveals splinter cult motives." }
      ]);
      setIsRunning(false);
    }, 800);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <label className="flex items-center gap-2">
          <span className="text-slate-300">Max Turns</span>
          <input
            type="number"
            min={1}
            max={20}
            defaultValue={10}
            className="w-20 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-right text-slate-100"
          />
        </label>
        <button
          type="button"
          className="rounded-md bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:opacity-60"
          disabled={isRunning}
          onClick={handleRun}
        >
          {isRunning ? "Simulating..." : "Run Session"}
        </button>
        <span className="text-xs text-slate-500">POST `/v1/sessions` → stream `/turns`</span>
      </div>

      <div className="max-h-72 overflow-y-auto rounded-lg border border-slate-800 bg-slate-950/80 p-4 text-sm">
        <ol className="space-y-3">
          {logs.map((entry) => (
            <li key={entry.turn} className="space-y-1">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="font-mono text-sky-300">Turn {entry.turn}</span>
                <span>{entry.actor}</span>
              </div>
              <p className="text-slate-200">{entry.content}</p>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
