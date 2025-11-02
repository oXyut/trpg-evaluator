import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { RunSessionPanel } from "../components/RunSessionPanel";

describe("RunSessionPanel", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("runs a session and renders turns and feedback", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: "scn_1", name: "Mystery" }]
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: "pc_1" })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: "sess_1" })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [
            {
              turn_index: 0,
              actor: "Keeper",
              role: "Keeper",
              content: "Keeper引用: 『地下室には禁断の儀式の痕跡が残る。』 を提示し、探索を促す。",
              references: ["scn_1#chunk_1"]
            }
          ]
        })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          summary: "参照チャンク数: 1/1 / シナリオとの整合性は概ね良好です。",
          metrics: {
            pacing: { score: 0.8, comment: "テスト" }
          }
        })
      } as Response);

    render(<RunSessionPanel />);

    const button = await screen.findByRole("button", { name: /Run Session/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Keeper引用/)).toBeInTheDocument();
    });

    expect(screen.getByText(/参照チャンク数/)).toBeInTheDocument();
    expect(fetchSpy).toHaveBeenCalledTimes(5);
  });
});
