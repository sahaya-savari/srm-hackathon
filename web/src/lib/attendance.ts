/**
 * attendance.ts — exact attendance mathematics + planning engine.
 *
 * Notation per subject:  A = attended so far, H = held so far, n = remaining classes,
 * target T = p/q (75% = 3/4, 90% = 9/10).
 *
 *   required x     = smallest x in [0, n] with (A + x) / (H + n) >= T
 *                  = max(0, ceil((p*(H+n) - q*A) / q))        feasible <=> x <= n
 *   safe absences  = n - x
 *   max possible   = (A + n) / (H + n)   (attend everything)
 *   min possible   = A / (H + n)         (attend nothing)
 *   IRREVERSIBLE   <=> max possible < 75%  <=> required x > n
 *
 * ALL comparisons use integer cross-multiplication, never floating point:
 * in floats 0.55 * 100 = 55.00000000000001, so Math.ceil would give 56 instead of 55.
 */

import { Section, countBySubject, addDays, sumCounts, CalendarOptions, SEMESTER_START, SEMESTER_END } from "./calendar";

export interface Target { p: number; q: number; label: string }
export const T75: Target = { p: 3, q: 4, label: "75%" };
export const T90: Target = { p: 9, q: 10, label: "90%" };

// ---------------------------------------------------------------- core maths
const ceilDiv = (a: number, b: number) => -Math.floor(-a / b); // exact for integers, b > 0

export function requiredClasses(A: number, H: number, n: number, T: Target): number {
  return Math.max(0, ceilDiv(T.p * (H + n) - T.q * A, T.q));
}

/** fraction >= T, exactly:  num/den >= p/q  <=>  q*num >= p*den */
const atLeast = (num: number, den: number, T: Target) => T.q * num >= T.p * den;

export const pct = (num: number, den: number): number | null => (den > 0 ? (num / den) * 100 : null);
export const round2 = (x: number | null) => (x === null ? null : Math.round(x * 100) / 100);

export type DetentionStatus = "LOCKED_SAFE" | "SAFE" | "CRITICAL" | "RECOVERING" | "IRREVERSIBLE" | "NO_DATA";
export type Goal90Status = "LOCKED" | "ACHIEVED" | "RECOVERABLE" | "IMPOSSIBLE" | "NO_DATA";
export type UiStatus = "SAFE" | "AT RISK" | "IRREVERSIBLE DETENTION" | "NO DATA";

/**
 * LOCKED_SAFE : ≥75% even if every remaining class is missed
 * SAFE        : currently ≥75% and can still miss at least one class
 * CRITICAL    : zero slack — must attend EVERY remaining class
 * RECOVERING  : currently <75% but can still reach 75%
 * IRREVERSIBLE: cannot reach 75% even attending every remaining class
 */
export function detentionStatus(A: number, H: number, n: number): DetentionStatus {
  if (H + n === 0) return "NO_DATA";
  if (!atLeast(A + n, H + n, T75)) return "IRREVERSIBLE";
  if (atLeast(A, H + n, T75)) return "LOCKED_SAFE";
  const slack = n - requiredClasses(A, H, n, T75);
  if (H > 0 && atLeast(A, H, T75)) return slack > 0 ? "SAFE" : "CRITICAL";
  return slack > 0 ? "RECOVERING" : "CRITICAL";
}

export function goal90Status(A: number, H: number, n: number): Goal90Status {
  if (H + n === 0) return "NO_DATA";
  if (!atLeast(A + n, H + n, T90)) return "IMPOSSIBLE";
  if (atLeast(A, H + n, T90)) return "LOCKED";
  if (H > 0 && atLeast(A, H, T90)) return "ACHIEVED";
  return "RECOVERABLE";
}

export const UI_STATUS: Record<DetentionStatus, UiStatus> = {
  LOCKED_SAFE: "SAFE", SAFE: "SAFE", CRITICAL: "AT RISK", RECOVERING: "AT RISK",
  IRREVERSIBLE: "IRREVERSIBLE DETENTION", NO_DATA: "NO DATA",
};

/** Consecutive classes that could be skipped RIGHT NOW while staying >= 75% at that moment. */
export function immediateSkipBudget(A: number, H: number): number {
  if (A === 0) return 0;
  return Math.max(0, Math.floor((T75.q * A - T75.p * H) / T75.p)); // floor(A/T - H)
}

// ---------------------------------------------------------------- percentage input
export interface PercentEstimate {
  held: number;
  attended: number;           // the value actually used (most conservative match)
  candidates: number[];       // every attended count that displays as the entered %
  consistent: boolean;        // false => entered % impossible with this many held classes
  warning: string | null;
}

/** Number of decimals the user typed ("83" -> 0, "83.3" -> 1, "83.33" -> 2). */
export function decimalsTyped(raw: string): number {
  const m = raw.trim().match(/\.(\d+)$/);
  return m ? Math.min(m[1].length, 2) : 0;
}

/**
 * A portal percentage is ROUNDED, so it does not uniquely identify attended/held.
 * Denominator = scheduled classes before today (assumes all were conducted).
 * Returns the LOWEST attended count consistent with the displayed % (never over-promise).
 * Exact integer maths in units of 1/1000 of a percent.
 */
export function estimateFromPercent(percent: number, held: number, decimals = 0): PercentEstimate {
  if (held <= 0) {
    return { held: 0, attended: 0, candidates: [], consistent: false, warning: "No classes of this subject have been scheduled yet." };
  }
  const P = Math.round(percent * 1000);
  const half = 500 / 10 ** decimals; // 500, 50, 5
  const cands: number[] = [];
  for (let a = 0; a <= held; a++) {
    const v = a * 100000; // a/held*100*1000, cross-multiplied by held
    if (((P - half) * held <= v && v < (P + half) * held) || (percent >= 100 && a === held)) cands.push(a);
  }
  if (cands.length === 0) {
    let near = 0;
    for (let a = 0; a <= held; a++) if (a * 100000 <= P * held) near = a; // round DOWN — conservative
    return {
      held, attended: near, candidates: [], consistent: false,
      warning: `${percent}% isn't possible with ${held} scheduled classes (closest below is ${near}/${held} = ${(near / held * 100).toFixed(1)}%). ` +
        `Your college probably held a different number of classes. Switch to "exact counts" for a precise answer.`,
    };
  }
  return {
    held, attended: cands[0], candidates: cands, consistent: true,
    warning: cands.length > 1
      ? `${percent}% could mean ${cands.map((a) => `${a}/${held}`).join(", ")} — using the safest (${cands[0]}/${held}).`
      : null,
  };
}

// ---------------------------------------------------------------- planning
export type InputMode = "percent" | "exact";
export interface SubjectInput {
  code: string;
  mode: InputMode;
  percent?: number;        // mode "percent"
  percentRaw?: string;     // as typed, to infer rounding decimals
  attended?: number;       // mode "exact"
  held?: number;
}
export type GapPolicy = "attend" | "miss";

export interface SubjectPlan {
  code: string;
  name: string;
  weeklyPeriods: number;
  mode: InputMode;
  estimate: PercentEstimate | null;
  attended: number;          // A as of today
  held: number;              // H as of today
  scheduledSoFar: number;    // timetable classes before today
  currentPct: number | null;
  gapClasses: number;        // classes between today and planning date (not yet happened)
  A: number;                 // attended at planning date (after gap policy)
  H: number;                 // held at planning date
  remaining: number;         // n = classes from planning date to semester end
  pctAtPlanningDate: number | null;
  required75: number | null; // null => impossible
  required90: number | null;
  safeAbsences75: number | null;
  safeAbsences90: number | null;
  maxPossible: number | null;
  minPossible: number | null;
  detention: DetentionStatus;
  uiStatus: UiStatus;
  goal90: Goal90Status;
  skipNow: number;
  explanation75: string;
  explanation90: string;
  otherGap: { policy: GapPolicy; required75: number | null; detention: DetentionStatus } | null;
  warnings: string[];
}

function explain(name: string, A: number, H: number, n: number, T: Target, isGoal: boolean): string {
  const x = requiredClasses(A, H, n, T);
  const mx = pct(A + n, H + n);
  if (H + n === 0) return `${name}: no classes scheduled.`;
  if (x > n) return `${name}: even attending all ${n} remaining classes only reaches ${mx!.toFixed(1)}% — below the ${T.label} ${isGoal ? "goal" : "minimum"}.`;
  if (atLeast(A, H + n, T)) return `${name}: you stay at or above ${T.label} even if you miss all ${n} remaining classes.`;
  return `${name}: attend at least ${x} of the ${n} remaining classes (you can miss up to ${n - x}) to finish at or above ${T.label}.`;
}

export function planSubject(section: Section, input: SubjectInput, elapsed: number, gap: number, n: number, policy: GapPolicy): SubjectPlan {
  const sub = section.subjects.find((s) => s.code === input.code)!;
  const warnings: string[] = [];
  let A = 0, H = 0, estimate: PercentEstimate | null = null;

  if (input.mode === "exact") {
    A = Math.max(0, Math.floor(input.attended ?? 0));
    H = Math.max(0, Math.floor(input.held ?? 0));
    if (A > H) { warnings.push("Attended can't be more than held — capped to held."); A = H; }
    if (H > elapsed + 5 || H < elapsed - 15) warnings.push(`The timetable shows ${elapsed} classes so far; you entered ${H}. That's fine if your college's count differs.`);
  } else {
    const p = Math.min(100, Math.max(0, input.percent ?? 0));
    if (p !== input.percent) warnings.push("Percentage must be between 0 and 100 — adjusted.");
    estimate = estimateFromPercent(p, elapsed, decimalsTyped(input.percentRaw ?? String(p)));
    A = estimate.attended; H = estimate.held;
    if (estimate.warning) warnings.push(estimate.warning);
  }

  const Aeff = A + (policy === "attend" ? gap : 0);
  const Heff = H + gap;
  const r75 = requiredClasses(Aeff, Heff, n, T75);
  const r90 = requiredClasses(Aeff, Heff, n, T90);
  const det = detentionStatus(Aeff, Heff, n);
  const other: GapPolicy = policy === "attend" ? "miss" : "attend";
  const Ao = A + (other === "attend" ? gap : 0);
  const r75o = requiredClasses(Ao, Heff, n, T75);

  return {
    code: sub.code, name: sub.name, weeklyPeriods: sub.weeklyPeriods, mode: input.mode, estimate,
    attended: A, held: H, scheduledSoFar: elapsed, currentPct: round2(pct(A, H)),
    gapClasses: gap, A: Aeff, H: Heff, remaining: n, pctAtPlanningDate: round2(pct(Aeff, Heff)),
    required75: r75 <= n ? r75 : null, required90: r90 <= n ? r90 : null,
    safeAbsences75: r75 <= n ? n - r75 : null, safeAbsences90: r90 <= n ? n - r90 : null,
    maxPossible: round2(pct(Aeff + n, Heff + n)), minPossible: round2(pct(Aeff, Heff + n)),
    detention: det, uiStatus: UI_STATUS[det], goal90: goal90Status(Aeff, Heff, n),
    skipNow: immediateSkipBudget(A, H),
    explanation75: explain(sub.name, Aeff, Heff, n, T75, false),
    explanation90: explain(sub.name, Aeff, Heff, n, T90, true),
    otherGap: gap > 0 ? { policy: other, required75: r75o <= n ? r75o : null, detention: detentionStatus(Ao, Heff, n) } : null,
    warnings,
  };
}

export interface PlanResult {
  ok: true;
  today: string;
  planningDate: string;
  classesLeftInSemester: number;       // all subjects, from planning date to 29 Nov
  subjects: SubjectPlan[];
  overall: SubjectPlan;                // aggregate across subjects (summed counts, NOT averaged %)
  overallStatus: UiStatus;             // worst subject wins
  irreversibleCount: number;
  atRiskCount: number;
}
export interface PlanError { ok: false; errors: string[] }

/**
 * today         : the user's real local date (localTodayISO() in the browser)
 * planningDate  : date the plan starts from (today <= planningDate <= 29 Nov 2026)
 * policy        : what to assume for classes between today and planningDate
 */
export function plan(section: Section, inputs: SubjectInput[], today: string, planningDate: string,
  policy: GapPolicy = "attend", opts: CalendarOptions = {}): PlanResult | PlanError {
  const errors: string[] = [];
  if (today < SEMESTER_START) errors.push("The semester starts on 29 Aug 2026 — nothing to calculate yet.");
  if (planningDate < today) errors.push("The planning date can't be in the past.");
  if (planningDate > SEMESTER_END) errors.push("The planning date must be on or before 29 Nov 2026 (semester end).");
  if (errors.length) return { ok: false, errors };

  const elapsed = countBySubject(section, SEMESTER_START, addDays(today, -1), opts);       // before today = held
  const gap = countBySubject(section, today, addDays(planningDate, -1), opts);             // today .. day before plan
  const remaining = countBySubject(section, planningDate, SEMESTER_END, opts);             // plan date .. end

  const subjects = inputs
    .filter((i) => section.subjects.some((s) => s.code === i.code))
    .map((i) => planSubject(section, i, elapsed[i.code] ?? 0, gap[i.code] ?? 0, remaining[i.code] ?? 0, policy));

  // Overall = sum of exact counts across subjects (TC18: weighted by classes, not an average of %).
  const sA = subjects.reduce((s, x) => s + x.attended, 0), sH = subjects.reduce((s, x) => s + x.held, 0);
  const gA = subjects.reduce((s, x) => s + x.A, 0), gH = subjects.reduce((s, x) => s + x.H, 0);
  const n = subjects.reduce((s, x) => s + x.remaining, 0);
  const r75 = requiredClasses(gA, gH, n, T75), r90 = requiredClasses(gA, gH, n, T90);
  const det = detentionStatus(gA, gH, n);
  const overall: SubjectPlan = {
    code: "OVERALL", name: "All subjects", weeklyPeriods: section.totalWeeklyPeriods, mode: "exact", estimate: null,
    attended: sA, held: sH, scheduledSoFar: subjects.reduce((s, x) => s + x.scheduledSoFar, 0), currentPct: round2(pct(sA, sH)),
    gapClasses: gH - sH, A: gA, H: gH, remaining: n, pctAtPlanningDate: round2(pct(gA, gH)),
    required75: r75 <= n ? r75 : null, required90: r90 <= n ? r90 : null,
    safeAbsences75: r75 <= n ? n - r75 : null, safeAbsences90: r90 <= n ? n - r90 : null,
    maxPossible: round2(pct(gA + n, gH + n)), minPossible: round2(pct(gA, gH + n)),
    detention: det, uiStatus: UI_STATUS[det], goal90: goal90Status(gA, gH, n), skipNow: immediateSkipBudget(sA, sH),
    explanation75: explain("Overall", gA, gH, n, T75, false), explanation90: explain("Overall", gA, gH, n, T90, true),
    otherGap: null, warnings: [],
  };

  const irreversibleCount = subjects.filter((s) => s.detention === "IRREVERSIBLE").length;
  const atRiskCount = subjects.filter((s) => s.uiStatus === "AT RISK").length;
  return {
    ok: true, today, planningDate, classesLeftInSemester: sumCounts(remaining), subjects, overall,
    overallStatus: subjects.length === 0 ? "NO DATA" : irreversibleCount ? "IRREVERSIBLE DETENTION" : atRiskCount ? "AT RISK" : "SAFE",
    irreversibleCount, atRiskCount,
  };
}

/** Points for the projection chart: best (attend all), worst (miss all), minimum path to 75% / 90%. */
export function trajectory(A: number, H: number, n: number) {
  const x75 = requiredClasses(A, H, n, T75), x90 = requiredClasses(A, H, n, T90);
  const pts = [];
  for (let k = 0; k <= n; k++) {
    const d = H + k;
    pts.push({
      k,
      best: d ? ((A + k) / d) * 100 : null,
      worst: d ? (A / d) * 100 : null,
      min75: d && x75 <= n ? ((A + Math.min(k, x75)) / d) * 100 : null,
      min90: d && x90 <= n ? ((A + Math.min(k, x90)) / d) * 100 : null,
    });
  }
  return pts;
}

/** What-if: attendance at semester end if the student misses the next `miss` classes and attends the rest. */
export function whatIf(A: number, H: number, n: number, miss: number) {
  const m = Math.min(Math.max(0, miss), n);
  const finalPct = pct(A + (n - m), H + n);
  return { missed: m, finalPct: round2(finalPct), status: detentionStatus(A + (n - m), H + n, 0) };
}
