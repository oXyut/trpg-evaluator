'use client';

import { useAuth } from "./AuthProvider";

export function AppHeader() {
  const { user, loading, signInWithGoogle, signOutFromFirebase } = useAuth();

  return (
    <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div className="text-lg font-semibold text-sky-400">TRPG Evaluator MVP</div>
        <div className="flex items-center gap-4 text-sm text-slate-400">
          <span>Spec-aligned prototype</span>
          <div className="h-5 w-px bg-slate-700" />
          {loading ? (
            <span className="text-xs text-slate-500">認証状態を確認中…</span>
          ) : user ? (
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-300">
                {user.displayName || user.email || "ログイン済み"}
              </span>
              <button
                type="button"
                onClick={() => void signOutFromFirebase()}
                className="rounded-md border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-200 transition hover:border-slate-500"
              >
                サインアウト
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => void signInWithGoogle()}
              className="rounded-md bg-sky-500 px-3 py-1 text-xs font-semibold text-slate-950 transition hover:bg-sky-400"
            >
              Googleでサインイン
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
