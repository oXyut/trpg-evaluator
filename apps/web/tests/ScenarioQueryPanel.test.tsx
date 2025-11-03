import { fireEvent, screen, waitFor } from "@testing-library/react";

import { ScenarioQueryPanel } from "../components/ScenarioQueryPanel";
import { renderWithAuth } from "./testUtils";

describe("ScenarioQueryPanel", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("loads scenarios and performs query", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { id: "scn_a", name: "Mystery" }
        ]
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          matches: [
            { chunk_id: "chunk_1", score: 0.42, content: "地下室には禁断の儀式" }
          ]
        })
      } as Response);

    renderWithAuth(<ScenarioQueryPanel />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Mystery")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/キーワード/), { target: { value: "地下室" } });
    fireEvent.click(screen.getByRole("button", { name: /チャンクを検索/ }));

    await waitFor(() => {
      expect(screen.getByText(/chunk_1/)).toBeInTheDocument();
    });

    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });

  test("handles query failure", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: "scn_a", name: "Mystery" }]
      } as Response)
      .mockResolvedValueOnce({ ok: false, status: 500 } as Response);

    renderWithAuth(<ScenarioQueryPanel />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Mystery")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/キーワード/), { target: { value: "地下室" } });
    fireEvent.click(screen.getByRole("button", { name: /チャンクを検索/ }));

    await waitFor(() => {
      expect(screen.getByText(/検索に失敗/)).toBeInTheDocument();
    });
  });
});
