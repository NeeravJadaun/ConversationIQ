import { render, screen } from "@testing-library/react";
import { HealthScoreCard } from "../src/components/dashboard/HealthScoreCard";
import type { OperatingProcedure } from "../src/types";

const baseOp: OperatingProcedure = {
  id: "OP-01",
  name: "Card Lock / Freeze",
  description: "Locks cards",
  health_score: 85,
  resolution_rate: 0.9,
  escalation_rate: 0.05,
  loop_rate: 0.02,
  avg_turn_count: 4,
  avg_sentiment_score: 0.8,
  conversation_count: 100,
  last_computed_at: new Date().toISOString(),
};

describe("HealthScoreCard", () => {
  it("renders score correctly", () => {
    render(<HealthScoreCard op={baseOp} />);
    expect(screen.getByText("85")).toBeInTheDocument();
  });

  it("shows green styling when score >= 80", () => {
    const { container } = render(<HealthScoreCard op={baseOp} />);
    expect(container.innerHTML).toContain("text-healthy");
  });

  it("shows red styling when score < 60", () => {
    const { container } = render(<HealthScoreCard op={{ ...baseOp, health_score: 45 }} />);
    expect(container.innerHTML).toContain("text-critical");
  });

  it("View Details link has correct href", () => {
    render(<HealthScoreCard op={baseOp} />);
    expect(screen.getByRole("link", { name: /view details/i })).toHaveAttribute("href", "/procedures/OP-01");
  });
});
