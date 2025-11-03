'use client';

import { useState } from "react";

const TRAITS = [
  { id: "risk_taking", label: "Risk Taking" },
  { id: "cooperation", label: "Cooperation" },
  { id: "curiosity", label: "Curiosity" },
  { id: "violence_avoidance", label: "Violence Avoidance" }
] as const;

type TraitKey = (typeof TRAITS)[number]["id"];

type PersonalityState = Record<TraitKey, number>;

export function PersonalitySliders() {
  const [state, setState] = useState<PersonalityState>({
    risk_taking: 0.5,
    cooperation: 0.5,
    curiosity: 0.5,
    violence_avoidance: 0.5
  });

  return (
    <div className="space-y-4">
      {TRAITS.map((trait) => (
        <div key={trait.id} className="space-y-2">
          <div className="flex items-center justify-between text-xs uppercase tracking-wide text-slate-400">
            <span>{trait.label}</span>
            <span className="font-mono text-sky-300">{state[trait.id as TraitKey].toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={state[trait.id as TraitKey]}
            onChange={(event) =>
              setState((prev) => ({ ...prev, [trait.id]: Number.parseFloat(event.target.value) }))
            }
            className="w-full accent-sky-400"
          />
        </div>
      ))}
      <p className="text-xs text-slate-500">
        Adjust sliders to tune AI player behavior. Values sync with <code>/v1/personalities/&lt;character_id&gt;</code> payloads.
      </p>
    </div>
  );
}
