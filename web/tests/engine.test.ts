// Run: npx tsx --test tests/engine.test.ts
// (Next.js project: fix the import paths to ../src/lib/... and ../src/data/...)
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { requiredClasses, detentionStatus, goal90Status, estimateFromPercent, plan, T75, T90, UI_STATUS, whatIf, type SubjectPlan } from "../src/lib/attendance";
import { countBySubject, sumCounts, SEMESTER_START, SEMESTER_END, localTodayISO, type TimetableData } from "../src/lib/calendar";

const data: TimetableData = JSON.parse(readFileSync(new URL("../src/data/timetables.json", import.meta.url), "utf8"));
const sec = (id: string) => data.sections.find((s) => s.id === id)!;
const maxPct = (A: number, H: number, n: number) => Math.round(((A + n) / (H + n)) * 10000) / 100;

test("hackathon spec case A: 80/100, 20 left -> max 83.33%, SAFE", () => {
  assert.equal(maxPct(80, 100, 20), 83.33);
  assert.equal(UI_STATUS[detentionStatus(80, 100, 20)], "SAFE");
  assert.equal(requiredClasses(80, 100, 20, T75), 10);
});
test("hackathon spec case B: 60/100, 40 left -> max 71.43%, IRREVERSIBLE", () => {
  assert.equal(maxPct(60, 100, 40), 71.43);
  assert.equal(detentionStatus(60, 100, 40), "IRREVERSIBLE");
  assert.ok(requiredClasses(60, 100, 40, T75) > 40);
});
test("hackathon spec case C: 70/100, 50 left -> max 80%, recoverable", () => {
  assert.equal(maxPct(70, 100, 50), 80);
  assert.equal(detentionStatus(70, 100, 50), "RECOVERING");
  assert.equal(requiredClasses(70, 100, 50, T75), 43);
});
test("float trap: 55% of 100 needs exactly 55, not 56", () => {
  assert.equal(requiredClasses(0, 0, 100, { p: 55, q: 100, label: "55%" }), 55);
});
test("boundaries: exactly 75% with nothing left is SAFE-ish, 1 below is IRREVERSIBLE", () => {
  assert.equal(detentionStatus(75, 100, 0), "LOCKED_SAFE");
  assert.equal(detentionStatus(74, 100, 0), "IRREVERSIBLE");
  assert.equal(detentionStatus(0, 0, 0), "NO_DATA");
  assert.equal(goal90Status(90, 100, 0), "LOCKED");
  assert.equal(requiredClasses(90, 100, 0, T90), 0);
});
test("must attend every class -> CRITICAL", () => {
  // 70/100, 20 left: need ceil(0.75*120 - 70) = 20 = n
  assert.equal(detentionStatus(70, 100, 20), "CRITICAL");
});
test("percentage is ambiguous -> most conservative count", () => {
  const e = estimateFromPercent(83, 30, 0); // 25/30 = 83.33
  assert.equal(e.attended, 25);
  const amb = estimateFromPercent(75, 100, 0); // 745..754 not possible; 75/100 only at 0 decimals? 74.5<=a<75.5 -> 75
  assert.deepEqual(amb.candidates, [75]);
  const imp = estimateFromPercent(83, 4, 0); // 3/4=75, 4/4=100 -> impossible
  assert.equal(imp.consistent, false);
  assert.equal(imp.attended, 3); // rounds DOWN
});
test("what-if never goes below 0 or above n", () => {
  assert.equal(whatIf(10, 10, 5, 99).missed, 5);
  assert.equal(whatIf(10, 10, 5, -3).missed, 0);
});
test("semester counts are positive for every section", () => {
  for (const s of data.sections) assert.ok(sumCounts(countBySubject(s, SEMESTER_START, SEMESTER_END)) > 100, s.id);
});
test("plan() rejects bad dates and never returns NaN", () => {
  const s = sec("III-ECE-B");
  const bad = plan(s, [], "2026-10-01", "2026-09-01");
  assert.equal(bad.ok, false);
  const r = plan(s, s.subjects.map((x) => ({ code: x.code, mode: "exact" as const, attended: 0, held: 0 })), "2026-10-01", "2026-10-01");
  assert.ok(r.ok);
  if (r.ok) assert.ok(!JSON.stringify(r).includes("NaN") && !JSON.stringify(r).includes("Infinity"));
  assert.match(localTodayISO(), /^\d{4}-\d{2}-\d{2}$/);
});
test("TypeScript engine matches the Python reference engine on 400 random plans", () => {
  const cases = JSON.parse(readFileSync(new URL("./python_reference_cases.json", import.meta.url), "utf8"));
  let checks = 0;
  for (const c of cases) {
    const r = plan(sec(c.section), c.inputs, c.today, c.planningDate, c.policy);
    assert.ok(r.ok, JSON.stringify(c));
    if (!r.ok) continue;
    assert.equal(r.classesLeftInSemester, c.classesLeft, `${c.section} ${c.today}->${c.planningDate}`);
    for (const e of c.expected) {
      const s: SubjectPlan = r.subjects.find((x: SubjectPlan) => x.code === e.code)!;
      const ctx = `${c.section} ${e.code} today=${c.today} plan=${c.planningDate}`;
      assert.equal(s.attended, e.attended, ctx + " attended");
      assert.equal(s.held, e.held, ctx + " held");
      assert.equal(s.remaining, e.remaining, ctx + " remaining");
      assert.equal(s.A, e.A, ctx + " A_eff");
      assert.equal(s.H, e.H, ctx + " H_eff");
      assert.equal(s.required75, e.required75, ctx + " req75");
      assert.equal(s.required90, e.required90, ctx + " req90");
      assert.equal(s.detention, e.detention, ctx + " detention");
      assert.equal(s.goal90, e.goal90, ctx + " goal90");
      assert.equal(s.maxPossible, e.maxPossible, ctx + " max");
      assert.equal(s.skipNow, e.skipNow, ctx + " skipNow");
      checks++;
    }
  }
  assert.ok(checks > 3000);
});
