import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import StatusBadge from "./status-badge";

describe("StatusBadge", () => {
  it("renders the status text and default tone", () => {
    render(<StatusBadge>Mock LLM</StatusBadge>);

    const status = screen.getByRole("status");
    expect(status.textContent).toContain("Mock LLM");
    expect(status.dataset.tone).toBe("neutral");
  });

  it("exposes an accessible label and semantic tone", () => {
    render(
      <StatusBadge label="Database state" tone="success">
        Connected
      </StatusBadge>,
    );

    expect(screen.getByLabelText("Database state").dataset.tone).toBe("success");
  });
});
