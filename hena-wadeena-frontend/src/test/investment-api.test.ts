import { describe, expect, it } from "vitest";
import { __investmentTestUtils } from "@/services/api";

describe("investment api mappers", () => {
  it("maps opportunity responses into frontend-friendly cards", () => {
    const opportunity = __investmentTestUtils.toOpportunity({
      id: "opp-1",
      owner_id: "owner-1",
      title: "Solar Valley Startup",
      category: "renewable_energy",
      opportunity_type: "startup",
      location: "Dakhla",
      min_investment: 3000000,
      max_investment: 7000000,
      investment_range: "3,000,000 - 7,000,000 EGP",
      expected_roi: "15-19%",
      description: "Clean energy startup for irrigation systems.",
      status: "open",
      is_verified: true,
      interest_count: 2,
      is_watchlisted: true,
      created_at: "2026-03-22T00:00:00Z",
      updated_at: "2026-03-22T00:00:00Z",
    });

    expect(opportunity.opportunity_type).toBe("startup");
    expect(opportunity.investment).toContain("EGP");
    expect(opportunity.is_watchlisted).toBe(true);
    expect(opportunity.interest_count).toBe(2);
  });

  it("maps dashboard payloads into nested opportunity and interest collections", () => {
    const dashboard = __investmentTestUtils.toDashboard({
      status_counts: { submitted: 1, under_review: 2 },
      recent_interests: [
        {
          id: "interest-1",
          opportunity_id: "opp-1",
          opportunity_title: "Integrated Farm Project",
          opportunity_category: "agriculture",
          opportunity_location: "Kharga",
          opportunity_type: "project",
          investor_id: "investor-1",
          message: "Please share the model.",
          contact_name: "Investor One",
          contact_email: "investor1@example.com",
          contact_phone: "+201000000001",
          company_name: "Oasis Capital",
          investor_type: "Fund",
          budget_range: "1-5M EGP",
          status: "submitted",
          owner_notes: undefined,
          created_at: "2026-03-22T00:00:00Z",
          updated_at: "2026-03-22T00:00:00Z",
        },
      ],
      watchlist: [
        {
          id: "opp-2",
          owner_id: "owner-1",
          title: "White Desert Retreat",
          category: "tourism",
          opportunity_type: "project",
          location: "Farafra",
          min_investment: 5000000,
          max_investment: 9000000,
          investment_range: "5,000,000 - 9,000,000 EGP",
          expected_roi: "18-24%",
          description: "Eco retreat opportunity.",
          status: "open",
          is_verified: true,
          interest_count: 3,
          is_watchlisted: true,
          created_at: "2026-03-22T00:00:00Z",
          updated_at: "2026-03-22T00:00:00Z",
        },
      ],
      recommended: [],
    });

    expect(dashboard.status_counts.under_review).toBe(2);
    expect(dashboard.recent_interests[0].opportunity_title).toBe("Integrated Farm Project");
    expect(dashboard.watchlist[0].title).toBe("White Desert Retreat");
  });
});
