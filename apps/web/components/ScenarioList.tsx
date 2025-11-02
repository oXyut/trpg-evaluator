'use client';

import { useEffect, useState } from "react";

type ScenarioSummary = {
  id: string;
  name: string;
  chunks?: Array<unknown>;
};

type LoadState = "idle" | "loading" | "error";

export function ScenarioList() {
  const [items, setItems] = useState<ScenarioSummary[]>([]);
  const [state, setState] = useState<LoadState>("loading");

  const load = async () => {
    setState("loading");
    try {
      const response = await fetch("/v1/scenarios");
      if (!response.ok) {
        throw new Error(`request failed: ${response.status}`);
      }
      const data: ScenarioSummary[] = await response.json();
      setItems(data);
      setState("idle");
    } catch (error) {
      console.error("Failed to load scenarios", error);
      setState("error");
    }
  };

  useEffect(() => {
    load();
    const handler = () => load();
    window.addEventListener("scenario:uploaded", handler);
    return () => {
      window.removeEventListener("scenario:uploaded", handler);
    };
  }, []);

  if (state === "loading" && items.length === 0) {
    return (
      <div className="rounded-md border border-slate-800 bg-slate-900/60 px-4 py-3 text-xs text-slate-400">
        シナリオ一覧を読み込んでいます...
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="rounded-md border border-red-500/40 bg-red-900/30 px-4 py-3 text-xs text-red-200">
        シナリオ一覧の取得に失敗しました
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-md border border-slate-800 bg-slate-900/60 px-4 py-3 text-xs text-slate-400">
        まだアップロードされたシナリオはありません
      </div>
    );
  }

  return (
    <ul className="space-y-2 text-sm text-slate-200">
      {items.map((item) => (
        <li key={item.id} className="rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-3">
          <div className="font-semibold text-sky-200">{item.name}</div>
          <div className="text-xs text-slate-400">
            ID: <span className="font-mono text-sky-300">{item.id}</span>
            {Array.isArray(item.chunks) ? `（チャンク数: ${item.chunks.length}）` : null}
          </div>
        </li>
      ))}
    </ul>
  );
}
