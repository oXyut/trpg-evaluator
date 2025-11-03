'use client';

import { ChangeEvent, useCallback, useEffect, useState } from "react";

import { useAuth } from "./AuthProvider";

type ScenarioSummary = {
  id: string;
  name: string;
};

type TurnLog = {
  turn_index: number;
  actor: string;
  role: string;
  content: string;
  references: string[];
};

type Feedback = {
  summary: string;
  metrics: Record<string, { score: number; comment: string }>;
};

export function RunSessionPanel() {
  const [isRunning, setIsRunning] = useState(false);
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [scenarioId, setScenarioId] = useState<string>("");
  const [maxTurns, setMaxTurns] = useState<number>(6);
  const [logs, setLogs] = useState<TurnLog[]>([]);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { token, user, loading } = useAuth();

  const loadScenarios = useCallback(async () => {
    if (!token) {
      return;
    }
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
          setScenarioId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load scenarios", err);
        setError("シナリオ一覧の取得に失敗しました");
      }
  }, [token]);

  useEffect(() => {
    if (!token) {
      if (!loading && !user) {
        setScenarios([]);
        setScenarioId("");
        setError(null);
      }
      return;
    }
    loadScenarios();
  }, [token, loadScenarios, loading, user]);

  const handleRun = async () => {
    if (!token) {
      setError("セッションを実行するにはログインしてください");
      return;
    }
    if (!scenarioId) {
      setError("シナリオを選択してください");
      return;
    }
    setIsRunning(true);
    setError(null);
    setLogs([]);
    setFeedback(null);

    try {
      const characterResponse = await fetch("/v1/characters", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ method: "random" })
      });
      if (!characterResponse.ok) {
        throw new Error("character creation failed");
      }
      const character = await characterResponse.json();

      const sessionPayload = {
        scenario_id: scenarioId,
        party_ids: [character.id],
        seed: Date.now() % 10_000,
        max_turns: maxTurns
      };

      const sessionResponse = await fetch("/v1/sessions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(sessionPayload)
      });
      if (!sessionResponse.ok) {
        throw new Error("session creation failed");
      }
      const session = await sessionResponse.json();

      const turnsResponse = await fetch(`/v1/sessions/${session.id}/turns`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      const turnsData = await turnsResponse.json();
      setLogs(turnsData.items ?? []);

      const feedbackResponse = await fetch(`/v1/sessions/${session.id}/feedback`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (feedbackResponse.ok) {
        setFeedback(await feedbackResponse.json());
      }
    } catch (err) {
      console.error("Failed to run session", err);
      setError("セッション実行に失敗しました");
    } finally {
      setIsRunning(false);
    }
  };

  const handleMaxTurnsChange = (event: ChangeEvent<HTMLInputElement>) => {
    setMaxTurns(Number.parseInt(event.target.value || "6", 10));
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <label className="flex items-center gap-2">
          <span className="text-slate-300">Scenario</span>
          <select
            className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
            value={scenarioId}
            onChange={(event) => setScenarioId(event.target.value)}
            disabled={isRunning || scenarios.length === 0 || !token}
          >
            {scenarios.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2">
          <span className="text-slate-300">Max Turns</span>
          <input
            type="number"
            min={1}
            max={20}
            value={maxTurns}
            onChange={handleMaxTurnsChange}
            className="w-20 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-right text-slate-100"
          />
        </label>
        <button
          type="button"
          className="rounded-md bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:opacity-60"
          disabled={isRunning || !scenarioId || !token}
          onClick={handleRun}
        >
          {isRunning ? "Running..." : "Run Session"}
        </button>
        <span className="text-xs text-slate-500">POST `/v1/sessions` → `/turns` → `/feedback`</span>
      </div>

      {(!loading && !user) ? (
        <div className="rounded border border-slate-800 bg-slate-900/60 px-3 py-2 text-xs text-slate-300">
          まず Google でサインインしてください。
        </div>
      ) : null}

      {error ? (
        <div className="rounded border border-red-500/40 bg-red-900/20 px-3 py-2 text-xs text-red-200">
          {error}
        </div>
      ) : null}

      <div className="max-h-72 overflow-y-auto rounded-lg border border-slate-800 bg-slate-950/80 p-4 text-sm">
        {logs.length === 0 ? (
          <p className="text-xs text-slate-500">セッションログはまだありません。</p>
        ) : (
          <ol className="space-y-3">
            {logs.map((entry) => (
              <li key={entry.turn_index} className="space-y-1">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span className="font-mono text-sky-300">Turn {entry.turn_index}</span>
                  <span>{entry.actor}</span>
                </div>
                <p className="text-slate-200">{entry.content}</p>
                {entry.references?.length ? (
                  <p className="text-xs text-slate-500">Refs: {entry.references.join(", ")}</p>
                ) : null}
              </li>
            ))}
          </ol>
        )}
      </div>

      {feedback ? (
        <div className="space-y-2 rounded-lg border border-slate-800 bg-slate-900/70 p-4 text-xs text-slate-300">
          <p className="text-slate-200">{feedback.summary}</p>
          <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {Object.entries(feedback.metrics).map(([key, metric]) => (
              <div key={key} className="flex flex-col gap-1">
                <dt className="font-semibold uppercase tracking-wide text-slate-400">{key}</dt>
                <dd className="text-slate-200">
                  <span className="font-mono text-sky-300 mr-2">{metric.score.toFixed(2)}</span>
                  {metric.comment}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      ) : null}
    </div>
  );
}
