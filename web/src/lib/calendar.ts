/**
 * calendar.ts — scheduled-class calendar for the Attendance Predictor.
 *
 * Pure functions, zero dependencies. All dates are ISO strings "YYYY-MM-DD" and all
 * date arithmetic is done in UTC so the result never shifts with the user's timezone.
 *
 * Counting unit: one timetable PERIOD = one attendance hour (a 2-period lab counts 2).
 * Only Monday–Friday are instruction days. Holidays can be passed in as ISO strings.
 */

export type Weekday = "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday";

export interface Slot {
  period: number;
  start: string;
  end: string;
  code: string;
  name: string;
  type: string;
  isLab: boolean;
  room: string | null;
  confidence: "high" | "medium" | "low";
}

export interface Subject {
  code: string;
  name: string;
  weeklyPeriods: number;
  classTypes: string[];
  faculty: string | null;
  credits: number | null;
  isCombinedBatchLab: boolean;
}

export interface Section {
  id: string;
  year: number;
  semester: number;
  department: string;
  venue: string | null;
  academicYear: string;
  sourceFile: string;
  isCurrentTimetable: boolean;
  note: string | null;
  totalWeeklyPeriods: number;
  subjects: Subject[];
  weekly: Record<Weekday, Slot[]>;
}

export interface TimetableData {
  meta: {
    semesterStart: string;
    semesterEnd: string;
    instructionDays: Weekday[];
    countingUnit: string;
    source: string;
    disclaimer: string;
  };
  sections: Section[];
}

export const SEMESTER_START = "2026-08-29";
export const SEMESTER_END = "2026-11-29";
const WEEKDAYS: (Weekday | null)[] = [null, "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", null]; // JS getUTCDay: 0=Sun

// ---------------------------------------------------------------- date helpers
export function parseISO(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}

export function toISO(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function addDays(iso: string, days: number): string {
  const d = parseISO(iso);
  d.setUTCDate(d.getUTCDate() + days);
  return toISO(d);
}

/** Today's date in the USER'S local timezone. Call this in the browser, never at build time. */
export function localTodayISO(now: Date = new Date()): string {
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function weekdayOf(iso: string): Weekday | null {
  return WEEKDAYS[parseISO(iso).getUTCDay()];
}

export function formatDate(iso: string): string {
  return parseISO(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
}

// ---------------------------------------------------------------- counting
export interface CalendarOptions {
  holidays?: Set<string>; // whole-day closures, ISO strings
}

/** Classes scheduled on one date (empty for weekends, holidays, or dates outside the semester). */
export function classesOn(section: Section, iso: string, opts: CalendarOptions = {}): Slot[] {
  if (iso < SEMESTER_START || iso > SEMESTER_END) return [];
  if (opts.holidays?.has(iso)) return [];
  const wd = weekdayOf(iso);
  return wd ? section.weekly[wd] : [];
}

/** Scheduled periods per subject for every date with from <= date <= to (inclusive). */
export function countBySubject(section: Section, from: string, to: string, opts: CalendarOptions = {}): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const s of section.subjects) counts[s.code] = 0;
  let d = from < SEMESTER_START ? SEMESTER_START : from;
  const last = to > SEMESTER_END ? SEMESTER_END : to;
  while (d <= last) {
    for (const slot of classesOn(section, d, opts)) counts[slot.code] = (counts[slot.code] ?? 0) + 1;
    d = addDays(d, 1);
  }
  return counts;
}

export function sumCounts(c: Record<string, number>): number {
  return Object.values(c).reduce((a, b) => a + b, 0);
}

/** Number of instruction days (Mon–Fri, not holidays) in [from, to]. */
export function instructionDays(from: string, to: string, opts: CalendarOptions = {}): number {
  let n = 0;
  let d = from < SEMESTER_START ? SEMESTER_START : from;
  const last = to > SEMESTER_END ? SEMESTER_END : to;
  while (d <= last) {
    if (weekdayOf(d) && !opts.holidays?.has(d)) n++;
    d = addDays(d, 1);
  }
  return n;
}
