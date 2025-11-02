import { Card } from "./Card";

const FEEDBACK = {
  summary: "Session reached climax within 10 turns. Focus on foreshadowing final twist earlier.",
  metrics: {
    pacing: { score: 0.78, comment: "Escalation steady but finale abrupt." },
    branching: { score: 0.64, comment: "Two optional leads remained unused." },
    difficulty: { score: 0.71, comment: "Skill thresholds align with party competencies." },
    fairness: { score: 0.82, comment: "Consequences telegraphed except for the final SAN loss." },
    cohesion: { score: 0.76, comment: "One subplot resolved off-screen." },
    tone: { score: 0.88, comment: "Eerie tone consistent; consider more sensory detail." }
  }
} as const;

export function FeedbackPanel() {
  return (
    <Card title="Feedback" description="GET `/v1/sessions/{id}/feedback`"> 
      <p className="text-sm text-slate-200">{FEEDBACK.summary}</p>
      <div className="grid gap-3 pt-3 sm:grid-cols-2">
        {Object.entries(FEEDBACK.metrics).map(([key, value]) => (
          <div key={key} className="rounded-lg border border-slate-800 bg-slate-950/40 p-4">
            <div className="flex items-center justify-between text-xs uppercase text-slate-400">
              <span>{key}</span>
              <span className="font-mono text-sky-300">{value.score.toFixed(2)}</span>
            </div>
            <p className="mt-2 text-sm text-slate-200">{value.comment}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
