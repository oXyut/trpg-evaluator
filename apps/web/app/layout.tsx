import "./globals.css";
import type { Metadata } from "next";
import { Providers } from "../components/Providers";
import { AppHeader } from "../components/AppHeader";

export const metadata: Metadata = {
  title: "TRPG Evaluator",
  description: "Upload and auto-evaluate Call of Cthulhu scenarios"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <Providers>
          <AppHeader />
          <main className="mx-auto max-w-6xl space-y-8 px-6 py-8">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
