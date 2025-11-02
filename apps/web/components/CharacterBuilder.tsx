'use client';

import { useState } from "react";

type Method = "random" | "point_buy" | "import";

export function CharacterBuilder() {
  const [method, setMethod] = useState<Method>("random");

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        {(
          [
            { value: "random", label: "Random" },
            { value: "point_buy", label: "Point Buy" },
            { value: "import", label: "Import JSON" }
          ] satisfies { value: Method; label: string }[]
        ).map((item) => (
          <button
            key={item.value}
            type="button"
            className={`rounded-md border px-4 py-2 text-sm transition ${
              method === item.value
                ? "border-sky-500 bg-sky-500/20 text-sky-100"
                : "border-slate-700 bg-slate-900/60 text-slate-400 hover:border-sky-500/40"
            }`}
            onClick={() => setMethod(item.value)}
          >
            {item.label}
          </button>
        ))}
      </div>

      {method === "random" ? (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4 text-xs text-slate-400">
          Stats roll using 3d6×5 (high for INT, SIZ, EDU). Derived values follow CoC7 rules. Endpoint: `/v1/characters`.
        </div>
      ) : null}

      {method === "point_buy" ? (
        <form className="grid gap-3 text-xs" aria-label="Point buy form">
          <label className="space-y-1">
            <span className="text-slate-300">Investigator Name</span>
            <input
              className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
              placeholder="Akiko Kuroiwa"
            />
          </label>
          <p className="text-slate-500">
            Provide stats JSON matching `packages/schema/characters.json`. Submit via `/v1/characters` with `method=point_buy`.
          </p>
        </form>
      ) : null}

      {method === "import" ? (
        <div className="space-y-2 text-xs text-slate-400">
          <p>
            Paste investigator JSON exported from external tools. API validates against shared schema and stores snapshot references.
          </p>
          <textarea
            className="min-h-[160px] w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200"
            placeholder='{"pc_name":"Yuto","stats":{...}}'
          />
        </div>
      ) : null}
    </div>
  );
}
