import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { ScenarioUploader } from "../components/ScenarioUploader";

describe("ScenarioUploader", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("uploads text files and displays scenario information", async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({ id: "scn_test", chunks: [1, 2, 3] })
    } as Response;
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(mockResponse);
    const eventListener = vi.fn();
    window.addEventListener("scenario:uploaded", eventListener);

    render(<ScenarioUploader />);

    const input = screen.getByLabelText(/Drop scenario/i) as HTMLInputElement;
    const mockFile = {
      name: "mystery.txt",
      type: "text/plain",
      text: vi.fn().mockResolvedValue("dummy content")
    } as unknown as File;

    fireEvent.change(input, { target: { files: [mockFile] } });

    expect(screen.getByText("mystery.txt")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/アップロード完了/)).toBeInTheDocument();
    });

    expect(screen.getByText(/scn_test/)).toBeInTheDocument();
    expect(screen.getByText(/チャンク数: 3/)).toBeInTheDocument();
    expect(fetchSpy).toHaveBeenCalledWith(
      "/v1/scenarios",
      expect.objectContaining({ method: "POST" })
    );
    expect(mockFile.text).toHaveBeenCalled();
    expect(eventListener).toHaveBeenCalledTimes(1);

    window.removeEventListener("scenario:uploaded", eventListener);
  });
});
