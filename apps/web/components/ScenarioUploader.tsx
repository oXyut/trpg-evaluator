'use client';

import { useState } from "react";

import { useAuth } from "./AuthProvider";

export function ScenarioUploader() {
  const [fileName, setFileName] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [scenarioId, setScenarioId] = useState<string | null>(null);
  const [chunkCount, setChunkCount] = useState<number | null>(null);
  const { token, user, loading, signInWithGoogle } = useAuth();

  const handleFileSelect = async (file: File) => {
    setFileName(file.name);
    setStatus("アップロード準備中...");
    setScenarioId(null);
    setChunkCount(null);

    try {
      const isTextLike =
        file.type.startsWith("text/") ||
        file.name.toLowerCase().endsWith(".md") ||
        file.name.toLowerCase().endsWith(".txt");

      if (!isTextLike) {
        setStatus("MVPではテキスト/Markdownのみ対応しています");
        return;
      }

      if (!token) {
        setStatus("アップロードにはログインが必要です");
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/v1/scenarios/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const message = await response.text();
        setStatus(`アップロード失敗: ${message || response.status}`);
        return;
      }

      const data: { id: string; chunks?: unknown[] } = await response.json();
      setScenarioId(data.id);
      setChunkCount(Array.isArray(data.chunks) ? data.chunks.length : null);
      setStatus("アップロード完了");

      window.dispatchEvent(new CustomEvent("scenario:uploaded", { detail: { id: data.id } }));
    } catch (error) {
      console.error("Scenario upload failed", error);
      setStatus("アップロード中にエラーが発生しました");
    }
  };

  if (!loading && !user) {
    return (
      <div className="space-y-3 rounded-md border border-slate-800 bg-slate-900/60 px-4 py-3 text-sm text-slate-300">
        <p>シナリオをアップロードするには Google でサインインしてください。</p>
        <button
          type="button"
          onClick={() => void signInWithGoogle()}
          className="rounded-md bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400"
        >
          サインイン
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <label
        htmlFor="scenario-upload"
        className="flex cursor-pointer items-center justify-center rounded-lg border border-dashed border-sky-500/40 bg-slate-900/40 px-6 py-10 text-center transition hover:border-sky-400"
      >
        <div>
          <p className="text-sm font-medium text-sky-300">Drop scenario PDF/MD/TXT</p>
          <p className="mt-2 text-xs text-slate-400">Vertex AI RAG ingestion kicks in automatically.</p>
        </div>
      </label>
      <input
        id="scenario-upload"
        type="file"
        accept=".pdf,.md,.txt"
        className="hidden"
        onChange={async (event) => {
          const file = event.target.files?.[0];
          if (!file) {
            return;
          }
          void handleFileSelect(file);
        }}
      />
      {fileName ? (
        <div className="rounded-md border border-slate-800 bg-slate-900/70 px-3 py-2 text-xs text-slate-300">
          <div className="font-mono text-sky-200">{fileName}</div>
          <div className="text-slate-500">{status}</div>
          {scenarioId ? (
            <div className="text-slate-500">
              シナリオID: <span className="font-mono text-sky-300">{scenarioId}</span>
              {typeof chunkCount === "number" ? `（チャンク数: ${chunkCount}）` : null}
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
