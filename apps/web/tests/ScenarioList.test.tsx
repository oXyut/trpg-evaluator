import { act } from "react";
import { screen, waitFor } from "@testing-library/react";

import { ScenarioList } from "../components/ScenarioList";
import { renderWithAuth } from "./testUtils";

describe("ScenarioList", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("renders fetched scenarios", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      {
        ok: true,
        json: async () => [
          { id: "scn_1", name: "Moonlight", chunks: [1, 2] },
          { id: "scn_2", name: "Forest", chunks: [] }
        ]
      } as Response
    );

    renderWithAuth(<ScenarioList />);

    await waitFor(() => {
      expect(screen.getByText("Moonlight")).toBeInTheDocument();
    });

    expect(screen.getByText("scn_1")).toBeInTheDocument();
    expect(screen.getByText("scn_2")).toBeInTheDocument();
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  test("reloads when scenario uploaded event fires", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: "scn_3", name: "Harbor", chunks: [] }]
      } as Response);

    renderWithAuth(<ScenarioList />);

    await waitFor(() => {
      expect(screen.getByText(/まだアップロード/)).toBeInTheDocument();
    });

    act(() => {
      window.dispatchEvent(new CustomEvent("scenario:uploaded", { detail: { id: "scn_3" } }));
    });

    await waitFor(() => {
      expect(screen.getByText("Harbor")).toBeInTheDocument();
    });

    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });

  test("shows error when fetch fails", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({ ok: false, status: 500 } as Response);

    renderWithAuth(<ScenarioList />);

    await waitFor(() => {
      expect(screen.getByText(/取得に失敗/)).toBeInTheDocument();
    });
  });
});
