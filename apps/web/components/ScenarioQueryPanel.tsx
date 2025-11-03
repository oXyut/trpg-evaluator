'use client';

import { FormEvent, useCallback, useEffect, useState } from "react";

import { useAuth } from "./AuthProvider";

type ScenarioSummary = {
  id: string;
  name: string;
};

type QueryMatch = {
  chunk_id: string;
  score: number;
  content: string;
};

type LoadState = "idle" | "loading" | "error";

type QueryState = "idle" | "searching" | "error";

export function ScenarioQueryPanel() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [scenarioId, setScenarioId] = useState<string>("");
  const [query, setQuery] = useState<string>("");
  const [matches, setMatches] = useState<QueryMatch[]>([]);
  const [queryState, setQueryState] = useState<QueryState>("idle");
  const { token, user, loading } = useAuth();

  const fetchScenarios = useCallback(async () => {
    if (!token) {
      return;
    }
      setLoadState("loading");
      try {
        const response = await fetch("/v1/scenarios", {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        if (!response.ok) {
          throw new Error(`request failed: ${response.status}`);
        }
        const data = (await response.json()) as ScenarioSummary[];
        setScenarios(data);
        if (data.length > 0) {
          setScenarioId((current) => current || data[0].id);
        }
        setLoadState("idle");
      } catch (error) {
        console.error("Failed to load scenario list", error);
        setLoadState("error");
      }
  }, [token]);

  useEffect(() => {
    if (!token) {
      if (!loading && !user) {
        setScenarios([]);
        setLoadState("idle");
      }
      return;
    }
    fetchScenarios();
  }, [token, fetchScenarios, user, loading]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!scenarioId || !query.trim() || !token) {
      return;
    }
    setQueryState("searching");
    setMatches([]);

    try {
      const response = await fetch(`/v1/scenarios/${scenarioId}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ query, top_k: 3 })
      });

      if (!response.ok) {
        throw new Error(`request failed: ${response.status}`);
      }

      const data = (await response.json()) as { matches: QueryMatch[] };
      setMatches(data.matches ?? []);
      setQueryState("idle");
    } catch (error) {
      console.error("Scenario query failed", error);
      setQueryState("error");
    }
  };

  if (!loading && !user) {
    return (
      <div className="rounded-md border border-slate-800 bg-slate-900/60 px-4 py-3 text-xs text-slate-400">
        シナリオ検索を利用するにはログインしてください
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <form className="space-y-3" onSubmit={handleSubmit}>
        <div className="grid gap-2 text-sm">
          <label className="text-slate-300" htmlFor="scenario-select">
            シナリオ
          </label>
          <select
            id="scenario-select"
            className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
            value={scenarioId}
            onChange={(event) => setScenarioId(event.target.value)}
            disabled={loadState !== "idle" || scenarios.length === 0}
          >
            {scenarios.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
          {loadState === "error" ? (
            <span className="text-xs text-red-300">シナリオ一覧の取得に失敗しました</span>
          ) : null}
        </div>

        <div className="grid gap-2 text-sm">
          <label className="text-slate-300" htmlFor="scenario-query">
            キーワード
          </label>
          <input
            id="scenario-query"
            className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例: 地下室"
          />
        </div>

        <button
          type="submit"
          className="rounded-md bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:opacity-60"
          disabled={queryState === "searching" || !scenarioId || !query.trim() || !token}
        >
          {queryState === "searching" ? "検索中..." : "チャンクを検索"}
        </button>

        {queryState === "error" ? (
          <div className="rounded border border-red-500/40 bg-red-900/20 px-3 py-2 text-xs text-red-200">
            検索に失敗しました
          </div>
        ) : null}
      </form>

      <div className="space-y-3">
        {matches.length === 0 ? (
          <p className="text-xs text-slate-500">該当するチャンクがありません。</p>
        ) : (
          <ol className="space-y-2">
            {matches.map((match) => (
              <li key={match.chunk_id} className="rounded border border-slate-800 bg-slate-900/60 p-3 text-sm text-slate-200">
                <div className="text-xs text-slate-400">
                  Chunk: {match.chunk_id} / Score: {match.score.toFixed(3)}
                </div>
                <div className="whitespace-pre-wrap text-slate-200">{match.content}</div>
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  );
}
