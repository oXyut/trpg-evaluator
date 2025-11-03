import { PropsWithChildren } from "react";

export function Card({ title, description, children }: PropsWithChildren<{ title: string; description?: string }>) {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/40 shadow">
      <header className="border-b border-slate-800 px-5 py-4">
        <h2 className="text-base font-semibold text-slate-100">{title}</h2>
        {description ? <p className="mt-1 text-sm text-slate-400">{description}</p> : null}
      </header>
      <div className="space-y-4 px-5 py-4 text-sm text-slate-300">{children}</div>
    </section>
  );
}
