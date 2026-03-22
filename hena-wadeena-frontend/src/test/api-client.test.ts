import { describe, expect, it, vi, afterEach } from "vitest";
import { __apiTestUtils, marketAPI } from "@/services/api";

describe("api client configuration", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("routes local production preview traffic to the gateway by default", () => {
    expect(
      __apiTestUtils.resolveApiBaseUrl("/api/v1", { protocol: "http:", hostname: "localhost", port: "8080" }, false)
    ).toBe("http://localhost:8000/api/v1");
  });

  it("keeps absolute API base URLs unchanged", () => {
    expect(
      __apiTestUtils.resolveApiBaseUrl(
        "https://api.hena-wadeena.com/api/v1/",
        { protocol: "https:", hostname: "app.hena-wadeena.com", port: "" },
        false
      )
    ).toBe("https://api.hena-wadeena.com/api/v1");
  });

  it("throws a clear error when a misrouted API call returns frontend HTML", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "content-type": "text/html; charset=utf-8" }),
      text: vi.fn().mockResolvedValue("<!DOCTYPE html><html><body>preview fallback</body></html>"),
    } as unknown as Response);

    await expect(marketAPI.getPrices()).rejects.toThrow(
      "API request returned HTML instead of JSON. Check VITE_API_BASE_URL or route /api/v1 through the backend gateway."
    );
  });
});
