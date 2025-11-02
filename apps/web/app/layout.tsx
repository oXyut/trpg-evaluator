import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "TRPG Evaluator",
  description: "Upload and auto-evaluate Call of Cthulhu scenarios"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <div className="text-lg font-semibold text-sky-400">TRPG Evaluator MVP</div>
            <nav className="text-sm text-slate-400">Spec-aligned prototype</nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl space-y-8 px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
