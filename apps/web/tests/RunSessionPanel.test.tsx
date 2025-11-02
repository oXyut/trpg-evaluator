import { act } from "react";
import { fireEvent, render, screen } from "@testing-library/react";

import { RunSessionPanel } from "../components/RunSessionPanel";

describe("RunSessionPanel", () => {
  test("appends a keeper log entry after simulation completes", async () => {
    vi.useFakeTimers();
    render(<RunSessionPanel />);

    const button = screen.getByRole("button", { name: /Run Session/i });
    act(() => {
      fireEvent.click(button);
    });
    expect(button).toBeDisabled();

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(screen.getByText(/splinter cult motives/i)).toBeInTheDocument();
    vi.useRealTimers();
  });
});
