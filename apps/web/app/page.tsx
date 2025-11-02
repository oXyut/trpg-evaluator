import { Card } from "../components/Card";
import { CharacterBuilder } from "../components/CharacterBuilder";
import { FeedbackPanel } from "../components/FeedbackPanel";
import { PersonalitySliders } from "../components/PersonalitySliders";
import { RunSessionPanel } from "../components/RunSessionPanel";
import { ScenarioList } from "../components/ScenarioList";
import { ScenarioUploader } from "../components/ScenarioUploader";

export default function Page() {
  return (
    <div className="space-y-8">
      <Card title="Scenario Upload" description="Upload PDF/MD/TXT for ingestion into Vertex AI RAG">
        <ScenarioUploader />
      </Card>

      <Card title="Stored Scenarios" description="一覧とチャンク数を確認">
        <ScenarioList />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Personality Vector" description="Sync slider values with /v1/personalities">
          <PersonalitySliders />
        </Card>
        <Card title="Character Builder" description="Generate or import investigators for the party">
          <CharacterBuilder />
        </Card>
      </div>

      <Card title="Session Runner" description="Trigger AI self-play and stream turn logs">
        <RunSessionPanel />
      </Card>

      <FeedbackPanel />
    </div>
  );
}
