import { render, screen } from "@testing-library/react";
import { OPHealthGrid } from "../src/components/dashboard/OPHealthGrid";
import type { OperatingProcedure } from "../src/types";

function op(index: number, score: number): OperatingProcedure {
  return {
    id: `OP-0${index}`,
    name: `Procedure ${index}`,
    description: "desc",
    health_score: score,
    resolution_rate: 0.8,
    escalation_rate: 0.1,
    loop_rate: 0.1,
    avg_turn_count: 4,
    avg_sentiment_score: 0.8,
    conversation_count: 10,
    last_computed_at: new Date().toISOString(),
  };
}

describe("OPHealthGrid", () => {
  it("renders 8 cards when given 8 OPs", () => {
    render(<OPHealthGrid procedures={[1, 2, 3, 4, 5, 6, 7, 8].map((n) => op(n, 80 + n))} />);
    expect(screen.getAllByRole("link", { name: /view details/i })).toHaveLength(8);
  });

  it("sorts by health score ascending", () => {
    render(<OPHealthGrid procedures={[op(1, 90), op(2, 45), op(3, 70)]} />);
    const names = screen.getAllByRole("heading", { level: 3 }).map((node) => node.textContent);
    expect(names).toEqual(["Procedure 2", "Procedure 3", "Procedure 1"]);
  });
});
