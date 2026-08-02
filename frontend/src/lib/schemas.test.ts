import { describe, expect, it } from "vitest";

import { registerSchema, searchSchema } from "./schemas";

describe("registerSchema", () => {
  it("accepts a strong matching password", () => {
    const result = registerSchema.safeParse({
      email: "student@example.com",
      username: "student_01",
      full_name: "Student",
      password: "Student123!",
      passwordConfirmation: "Student123!",
    });
    expect(result.success).toBe(true);
  });

  it("rejects mismatched passwords", () => {
    const result = registerSchema.safeParse({
      email: "student@example.com",
      username: "student_01",
      password: "Student123!",
      passwordConfirmation: "Other123!",
    });
    expect(result.success).toBe(false);
  });
});

describe("searchSchema", () => {
  it("rejects an inverted year interval", () => {
    const result = searchSchema.safeParse({ query: "graph learning", fromYear: 2025, toYear: 2020 });
    expect(result.success).toBe(false);
  });
});
