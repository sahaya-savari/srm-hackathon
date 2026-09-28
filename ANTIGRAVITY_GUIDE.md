# Attendance Predictor — Complete Build Guide for Antigravity

**Event:** VibeCraft 2026 (Neuro Tech Titans × YUVA'26, SRM IST Tiruchirappalli) — Round 1 "The Overworld", Phase 1
**Build:** a polished, mobile-friendly Next.js web app that tells a student exactly how many classes they must attend.
**Read this whole file before writing any code.** Everything you need is in this kit; do not invent data.

---

## 0. Kit contents (already done for you — reuse, do not rewrite)

| Path | What it is | Status |
|---|---|---|
| `data/timetables.json` | All 13 sections from the 10 organiser PDFs: subjects, weekly periods, day-by-day slots with times | Hand-transcribed from image-only scans and visually verified cell by cell. **Do not OCR the PDFs again.** |
| `lib/calendar.ts` | Date helpers + counts scheduled classes per subject between any two dates | Tested |
| `lib/useToday.ts` | Hydration-safe React hook that returns today's date from the user's device (null during build/SSR) | Verified in a Next.js 16 production build |
| `lib/attendance.ts` | All attendance maths: required classes, statuses, percentage estimation, `plan()`, `trajectory()`, `whatIf()` | Tested: 11 tests, including **3,658 per-subject cross-checks** against an independently tested Python engine |
| `tests/engine.test.ts` + `tests/python_reference_cases.json` | The test suite | Must stay green |
| `styles/globals.css` | Tailwind v4 theme with the official VibeCraft colours, pixel buttons, irreversible-alert animation | Ready to drop in |

**Already verified:** this kit was dropped into a fresh `create-next-app@latest` project (Next.js 16.3, React 19.2, Tailwind 4). Tests pass, `tsc` is clean, `npm run lint` is clean, `npm run build` succeeds, and the built page shows the live device date.

**Rule: the UI calls the engine, it never re-implements the maths.** If you think the engine is wrong, write a failing test first and show it to the user. Don't edit the engine silently.

---

## 1. The official problem (from vibecraft-ntt-yuva26.vercel.app/round/1)

> College students often lose track of how many classes they actually have to attend. Portals don't tell them how many classes they must attend to stay above 90%, to recover from the detention zone (75%), or to avoid falling into it.
>
> **Build a smart attendance dashboard** for a college whose semester runs **29 Aug 2026 → 29 Nov 2026**, using the timetables of 10 class sections.
>
> **Phase 1 — The Core Calculator.** A student **selects their class section** and **enters their current attendance percentage** for their subjects. The site must **work out today's date** and also **ask for a preferred future date for planning**, then calculate:
> 1. How many total classes are left in the semester.
> 2. Exactly how many of those remaining classes the student must attend to stay out of the danger zone (75%).
> 3. If applicable, how many classes they must attend to stay above or reach 90%.
> 4. **The warning system:** if recovery before November is mathematically impossible, **loudly warn them with an "Irreversible Detention" alert.**
>
> Phase 2 is sealed and revealed later. Submission is at the end of Phase 2, so **keep the code easy to extend** (see §12).

### How it's judged (from the VibeCraft home page) and what that means for the build

| Judging criterion | What we build to win it |
|---|---|
| Relevance to the problem statement | The three answers (classes left, must-attend for 75%, must-attend for 90%) are the **first thing on the results screen**, in the organiser's own words. The "Irreversible Detention" alert uses that exact phrase. |
| Feasibility | Works offline in the browser, instant results, no backend, no login, deployable to Vercel in one click. |
| How well you used the given dataset | Every section is selectable. A **Timetable page** shows each section's real weekly grid and how many classes each subject has. Counts come from real class-by-class dates, not "weeks × average". |
| User experience and solution design | Three-step flow, mobile-first, plain-language explanations, a what-if slider, polished VibeCraft theme. |
| Technical Tasks round | Not part of the build. |

**Product thesis (say this in the demo):** *"We didn't build an attendance calculator. We built a decision engine that tells a student exactly how much recovery room they have before detention becomes mathematically unavoidable."*

---

## 2. Non-negotiable rules

1. **Today's date is read live from the user's browser** with the `useToday()` hook from `lib/useToday.ts`. Never hardcode a date. **Never compute it on the server or at build time.** Next.js pre-renders pages at build time, so a date computed there would be frozen forever. Don't use `useEffect(() => setToday(...))` either: Next.js 16's ESLint rule `react-hooks/set-state-in-effect` fails on it.
2. **Percentage input is the primary mode**, because the problem statement says so. Also offer an **"I know my exact counts"** toggle per subject (attended + held). Percentage mode must say it's an estimate, because a rounded percentage doesn't pin down the real counts. The engine picks the safest (lowest) matching count and returns a warning. Show that warning.
3. **75% and 90% are two separate indicators.** Never merge them into one score. Detention safety (SAFE / AT RISK / IRREVERSIBLE DETENTION) is the big one; the 90% goal (ACHIEVED / LOCKED / REACHABLE / NOT REACHABLE) is a separate, smaller badge.
4. **Irreversible Detention must be proven, not guessed.** Show the proof: *"Even if you attend all 9 remaining classes: (0 + 9) ÷ (4 + 9) = 69.23%, which is below 75%."*
5. **Never show NaN, Infinity, negative counts, or "undefined".** The engine returns `null` for "not possible". Render `null` as "Not possible" or "—" with an explanation.
6. **Say "scheduled".** The timetable tells us scheduled classes, not guaranteed ones. Wording: "36 scheduled classes left according to your timetable." Keep a short disclaimer in the footer.
7. **Overall attendance = total attended ÷ total held**, never an average of subject percentages. `plan()` already returns this as `overall`.
8. **Display rounding only.** Show 2 decimals. Never round a number and then feed it back into a calculation.
9. **No ML, no chatbot, no login, no database, no API routes** in Phase 1. It's deterministic maths.
10. All 13 sections must be selectable. The 4 first-year sections come from a PDF whose header says 2024-25. Show them with a small note (`section.note`) rather than hiding them, because judges will test "all sections".

---

## 3. Tech stack (keep it light)

- **Next.js, latest stable** (`npx create-next-app@latest`; verified with 16.3), **App Router**, **TypeScript (strict)**, **Tailwind CSS v4**, ESLint, `src/` directory, import alias `@/*`.
- **recharts** for charts. **lucide-react** for icons. **motion** (Framer Motion) is optional, for small transitions only.
- No UI kit is required. If you want one, shadcn/ui is fine, but restyle it to the VibeCraft theme.
- **tsx** runs `tests/engine.test.ts` with Node's built-in test runner: `npx tsx --test tests/engine.test.ts`. No test framework is needed.
- Fonts via **`@fontsource/press-start-2p` and `@fontsource/rubik`** (self-hosted npm packages). **Don't use `next/font/google`:** it downloads fonts during `npm run build` and the build fails if Google Fonts can't be reached (venue Wi-Fi, proxies). `globals.css` already sets the font families.
- Deploy target: **Vercel**. The whole app is client-side and can also be a static export.

### Setup commands
```bash
npx create-next-app@latest attendance-predictor --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --yes
cd attendance-predictor
npm i recharts lucide-react motion @fontsource/press-start-2p @fontsource/rubik
npm i -D tsx
# copy the kit in:
#   kit/data/timetables.json -> src/data/timetables.json
#   kit/lib/*.ts              -> src/lib/
#   kit/styles/globals.css    -> src/app/globals.css (replace the generated one)
#   kit/tests/*               -> tests/  (change "../lib/" to "../src/lib/" and "../data/" to "../src/data/")
npx tsx --test tests/engine.test.ts   # must print: pass 11, fail 0
```
Then replace the generated `src/app/layout.tsx` font imports (remove the Geist `next/font/google` imports and the `geistSans.variable` / `geistMono.variable` classNames on `<body>`) with:
```tsx
import "@fontsource/press-start-2p";
import "@fontsource/rubik/400.css"; import "@fontsource/rubik/500.css";
import "@fontsource/rubik/600.css"; import "@fontsource/rubik/700.css"; import "@fontsource/rubik/800.css";
import "./globals.css";
```
Import JSON with a type: `import raw from "@/data/timetables.json"; const data = raw as unknown as TimetableData;` (`resolveJsonModule` is on by default in create-next-app).

---

## 4. Data model (what is in `timetables.json`)

```ts
data.meta = { semesterStart: "2026-08-29", semesterEnd: "2026-11-29", instructionDays: Mon–Fri, countingUnit, source, disclaimer }
data.sections[] = {
  id: "III-ECE-B", year: 3, semester: 5, department: "ECE", venue: "IST 2xx", academicYear: "2026-27",
  sourceFile: "III ECE B.pdf", isCurrentTimetable: true, note: null | string,
  totalWeeklyPeriods: 27,
  subjects: [{ code: "21MAB302T", name: "Discrete Mathematics", weeklyPeriods: 4, classTypes: ["theory"],
               faculty: "…", credits: 4, isCombinedBatchLab: false }],   // sorted by weeklyPeriods desc
  weekly: { Monday: [{ period: 1, start: "09:00", end: "09:50", code, name, type, isLab, room, confidence }], … }
}
```

Sections: **II-BME, II-ECE-DS-A, II-ECE-DS-B, III-BME, III-ECE-A, III-ECE-B, III-ECE-DS, IV-ECE-A, IV-ECE-B** (2026-27) and **I-ECE-A, I-ECE-B-EEE, I-ECE-DS, I-BIOTECH-B-BME** (from the I-year PDF).

Counting rules, already built into the engine (document them on the Methodology page):
- **1 timetable period = 1 attendance hour.** A 2-period lab counts as 2 classes.
- Classes happen **Monday–Friday only**. Saturdays and Sundays have none.
- **Classes before today count as "held so far". Today's classes and later count as "remaining".**
- Remaining classes are counted **from the planning date through 29 Nov 2026**, date by date from the real weekly grid.
- A few cells are shared batch labs (codes containing `|`, e.g. in II-BME). They are kept as their own subject so nothing is double-counted.
- No holiday list was provided, so none are assumed. The engine accepts `opts.holidays` (a `Set` of ISO dates) if you add an "exclude holidays" feature later.

---

## 5. Engine API — the only functions the UI needs

```ts
import { plan, whatIf, trajectory, T75, T90, type SubjectInput, type PlanResult } from "@/lib/attendance";
import { formatDate, countBySubject, classesOn, addDays, SEMESTER_END, type Section } from "@/lib/calendar";
import { useToday } from "@/lib/useToday";   // const today = useToday(); // null until mounted in the browser

const inputs: SubjectInput[] = [
  { code: "21MAB302T", mode: "percent", percent: 50, percentRaw: "50" },   // percentRaw = exactly what the user typed
  { code: "21LEM301T", mode: "exact", attended: 0, held: 4 },
];
const result = plan(section, inputs, today, planningDate, gapPolicy /* "attend" | "miss" */);
if (!result.ok) showErrors(result.errors);
```

`result` (when `ok`) contains:
- `classesLeftInSemester`: **answer #1**, all scheduled classes from the planning date to 29 Nov.
- `subjects[]`, one `SubjectPlan` per subject:
  - `remaining`: this subject's scheduled classes left.
  - `required75`: **answer #2**, the minimum to attend for ≥75% (`null` means impossible).
  - `required90`: **answer #3**, the minimum to attend for ≥90% (`null` means impossible).
  - `safeAbsences75` / `safeAbsences90`: how many can still be missed.
  - `maxPossible` / `minPossible`: final % if all / none of the remaining classes are attended.
  - `currentPct`, `attended`, `held`, `pctAtPlanningDate`, `A`, `H`, `gapClasses`.
  - `detention` (internal: LOCKED_SAFE, SAFE, CRITICAL, RECOVERING, IRREVERSIBLE) and `uiStatus` (**what you display**: SAFE, AT RISK, IRREVERSIBLE DETENTION).
  - `goal90` (LOCKED, ACHIEVED, RECOVERABLE, IMPOSSIBLE).
  - `skipNow`: classes they could skip in a row right now and still be ≥75%.
  - `explanation75`, `explanation90`: ready-made plain-English sentences. Use them.
  - `estimate`: percentage-mode details (`candidates`, `warning`). `warnings[]`: show these next to the subject.
  - `otherGap`: when the planning date is after today, the result under the *opposite* assumption about the classes in between. Show it as "If you miss the classes until then: …".
- `overall`: the same shape, aggregated correctly across all subjects.
- `overallStatus`: the worst subject wins. `irreversibleCount`, `atRiskCount`.

Errors `plan()` returns: planning date before today; planning date after 29 Nov 2026; today before 29 Aug 2026. Validate the date picker (`min = today`, `max = 2026-11-29`) so users rarely hit them, but still render `result.errors` if they do.

**If today is after 29 Nov 2026** (for example, a judge looks later): `plan()` still works with `remaining = 0`. Show a banner: "The semester has ended. Showing your final standing."

### Status → UI mapping

| Engine | Show as | Colour token | Icon (lucide) |
|---|---|---|---|
| LOCKED_SAFE | **SAFE** + "Locked in: you're safe even if you miss every remaining class" | `grass-light` | `ShieldCheck` |
| SAFE | **SAFE** | `grass-light` | `ShieldCheck` |
| RECOVERING | **AT RISK** + "Below 75% now, but recoverable" | `torch` | `TriangleAlert` |
| CRITICAL | **AT RISK** + "You must attend every remaining class" | `torch` | `TriangleAlert` |
| IRREVERSIBLE | **IRREVERSIBLE DETENTION** | `tnt` | `Skull` or `OctagonX` |
| goal90 ACHIEVED / LOCKED | "90% goal: on track" / "90% locked in" | `ender-light` | `Target` |
| goal90 RECOVERABLE | "90% goal: reachable. Attend X of N" | `ender` | `Target` |
| goal90 IMPOSSIBLE | "90% goal: no longer reachable (max N%)" | `parchment-dim` | `Target` |

Never rely on colour alone. Always pair it with text and an icon.

---

## 6. Pages and user flow

### 6.1 Site map
```
/                      Landing: hero, "Check my attendance" CTA, 3-step explainer, stats strip
/planner               The app (3 steps + results), all on one page
/timetable             Section picker → weekly grid for the chosen section (?section=III-ECE-B)
/how-it-works          Methodology: formulas, assumptions, scheduled vs actual, data provenance
```
A shared header: logo "ATTENDANCE PREDICTOR" in Press Start 2P, nav links, and a small "VibeCraft 2026 · Round 1" tag. A shared footer with the disclaimer and "Today: 28 Sep 2026 (from your device clock)".

### 6.2 `/` Landing
- Hero: pixel headline **"Will you make 75%?"**, subtext *"Pick your section, enter your attendance, and see exactly how many classes you can miss before 29 Nov 2026."*, a big `.btn-block` CTA "Check my attendance →", and a secondary link "View timetables".
- A strip of live stats computed from the data and today's date: "**13** sections · **120** subjects · **N** days left in the semester · semester progress bar (29 Aug → 29 Nov, with a 'today' marker)".
- Three cards: "1. Pick your section", "2. Enter your attendance", "3. Get your plan".
- Background: the night colour with a subtle pixel grass strip at the bottom (CSS only, no images needed).

### 6.3 `/planner` — the core (this is where the judging happens)

Build it as **one client component tree** (`"use client"`) with state in `useReducer`. Layout: on desktop, inputs on the left (sticky, about 420px) and results on the right; on mobile, stacked, with a sticky bottom bar showing the overall status chip and a "See results ↓" button.

**Hydration-safe today:**
```tsx
const today = useToday();                 // from @/lib/useToday — null during build/SSR
if (!today) return <PlannerSkeleton />;   // real date appears instantly in the browser; rolls over at midnight
```

**Step 1 — Your section**
- Section cards grouped by year (IV, III, II, I). Each card shows the id, department, "27 classes/week", and "9 subjects". I-year cards get a small "2024-25 timetable" tag with a tooltip showing `section.note`.
- Also a searchable select for speed. The chosen section is stored in the URL (`/planner?section=III-ECE-B`) so the demo can deep-link.

**Step 2 — Your attendance**
- One row per subject: name, code, "4 classes/week", a percentage input (0–100, `inputMode="decimal"`, step 0.01), and a toggle "Exact counts". When on, the row shows two number inputs, *Attended* and *Held*, with the hint "Timetable says ~16 held so far".
- A **"Set all to __%"** helper at the top for speed, plus "Clear".
- Live validation under each input: out of range, attended > held, empty. Invalid rows are excluded from results with a visible message. The page never crashes.
- Under each percentage row, show the estimate in small dim text: "≈ 12 of 16 classes (estimate)". Show `warnings` in torch colour.
- Persist inputs per section in `localStorage` (wrap every access in try/catch) so a refresh doesn't wipe them.

**Step 3 — Plan from**
- Date picker: `min = today`, `max = 2026-11-29`, default today. Quick chips: "Today", "Next Monday", "1 Oct", "1 Nov", "Last week of semester". Disable any chip that is in the past.
- Show today prominently: "Today is Mon, 28 Sep 2026 (from your device)".
- If planning date > today, show a radio: **"Between now and then I will: ◉ attend all classes ○ miss all classes"** (maps to `gapPolicy` "attend"/"miss"), with "X classes happen before your planning date."

**Results** (recompute live on every change; no "Calculate" button is needed, but a "Calculate" button that scrolls to results is fine for the demo)

1. **Irreversible Detention alert** (only when `irreversibleCount > 0`). Full-width, top of results, class `alert-irreversible`, `role="alert"`, `aria-live="assertive"`, TNT red background, parchment text.
   - Title in Press Start 2P: **"⚠ IRREVERSIBLE DETENTION"**
   - Body: "Even if you attend every remaining class, you cannot reach 75% in **N subject(s)** before 29 Nov 2026."
   - For each such subject, the proof line: "Indian Art Form: (0 + 9) ÷ (4 + 9) = **69.23%** < 75%".
   - A calm next step: "Talk to your faculty advisor or HOD now about condonation or medical/OD options. Keep attending: your other subjects still count."
2. **Overall status banner.** A big chip with SAFE / AT RISK / IRREVERSIBLE DETENTION, overall current % and % at planning date, plus the separate 90% badge.
3. **The three answers as KPI cards**, in the organiser's words:
   - "Classes left in the semester": `classesLeftInSemester` (subtitle "scheduled, from {planning date} to 29 Nov").
   - "Must attend to stay above 75%": `overall.required75` of `overall.remaining` (or "Not possible").
   - "Must attend to reach/keep 90%": `overall.required90` of `overall.remaining` (or "Not possible", with the max %).
   - "Can still miss (75%)": `overall.safeAbsences75`.
   - "Best possible final %": `overall.maxPossible`.
   - "Subjects at risk": `atRiskCount + irreversibleCount` of `subjects.length`.
   Use a count-up animation on numbers (≤400ms, disabled for reduced motion).
4. **Subject cards** (grid, 1 column on mobile, 2–3 on desktop), sorted worst first (IRREVERSIBLE, then CRITICAL, RECOVERING, SAFE, LOCKED_SAFE, then lowest `safeAbsences75`). Each card has:
   - Name, code, status chip, 90% badge.
   - A horizontal bar: current % fill, with tick marks at 75% (torch) and 90% (ender), and a ghost segment up to `maxPossible`.
   - A plain recovery plan: **"Need 31 of 36 · Can miss 5 · Best possible 84.62%"**.
   - The `explanation75` sentence, and `explanation90` under a "90% goal" disclosure.
   - Percentage-mode estimate / warnings in small text.
   - If `otherGap` exists: "If you miss classes until {date}: {status}".
5. **Charts** (recharts, themed: parchment axes, night-2 panel, no gridline clutter):
   - **Subject bar chart**: horizontal bars of current %, reference lines at 75 and 90, bar colour by status, plus a marker for max possible.
   - **Projection line chart** for the focused subject or overall: `trajectory(A, H, remaining)`. Lines: "Attend everything" (grass), "Miss everything" (tnt, dashed), "Minimum to stay at 75%" (torch), "Minimum for 90%" (ender). X axis: "classes from {planning date}". Reference lines at 75/90.
   - Optional (P2): a **weekly heat strip**, Mon–Fri × periods for the section, coloured by the subject's status.
6. **What-if simulator.** Choose a subject (or Overall), then a slider "If I miss the next __ classes (and attend the rest)". It shows the resulting final %, the status, and a sentence. Also show quick chips for 1/2/3/4/5 misses as a small table. Use `whatIf(A, H, remaining, miss)`. Label as an estimate when in percentage mode.
7. **This week at a glance.** From `classesOn(section, date)` for today through Friday: a list of upcoming classes per day, each tagged with its subject status. Title: "Prioritise these: they're in your riskiest subjects." Sort by the subject's headroom, not by guesswork.
8. **Smart metrics** in plain language (one line each): "Riskiest subject: …", "Least room to miss: … (can miss 2)", "Fewest classes left: …", "Classes today: N", "Classes left this week: N".
9. **Share/print**: a "Copy summary" button that copies a plain-text summary; `window.print()` with a print stylesheet (optional).

### 6.4 `/timetable`
- Section picker (same cards), then a **Mon–Fri × periods grid** with times from the slots. Each cell shows the subject short name and code, lab cells span their periods visually, and low/medium-confidence cells get a small dot with the tooltip "Verified from a hand-written or faded cell".
- Below: a table of subjects with weekly periods, faculty, total scheduled classes this semester, classes held so far, and classes remaining (from `countBySubject`).
- A "Plan with this section →" button linking to `/planner?section=…`.
- This page is our proof for **"how well you used the dataset"**.

### 6.5 `/how-it-works`
Short, scannable sections:
- The formulas (render with plain HTML, no LaTeX library needed):
  `required = ceil(T × (H + R) − A)`, limited to 0…R · `max possible = (A + R) ÷ (H + R)` · `Irreversible ⇔ max possible < 75%` · `safe absences = R − required`.
- Why we use exact integer maths (in JavaScript `0.55 * 100` is `55.00000000000001`, so `Math.ceil` would wrongly say 56).
- Why percentages are estimates (75% could be 3/4, 6/8, 15/20, 30/40).
- Counting rules (§4), scheduled vs actual, no holiday data provided.
- Data provenance: the 10 PDFs were image-only scans, OCR matched only about 44% of subject codes, so every cell was hand-transcribed and visually verified.

---

## 7. Design system (match the VibeCraft site)

Tokens are in `styles/globals.css` (copied from the official site's CSS variables).

| Token | Hex | Use |
|---|---|---|
| night / night-2 / night-3 | #0B0E1F / #141A35 / #1C2448 | page / cards / inputs |
| parchment / parchment-dim | #F1E9D2 / #CFC6A9 | text / secondary text |
| torch / torch-light | #FF9130 / #FFB35C | primary buttons, AT RISK |
| grass-light / grass / grass-dark | #6FA043 / #4C7A2E / #345319 | SAFE |
| tnt | #E33D2E | IRREVERSIBLE DETENTION |
| ender / ender-light | #7C4DFF / #A88BFF | 90% goal |
| ink | #1B140C | text on torch buttons |

- **Type:** Press Start 2P only for headings, section labels, status words and big KPI numbers (it's hard to read at small sizes; minimum 12px, line-height 1.6). Everything else in Rubik. Numbers use the `.num` class (tabular figures).
- **Shape:** square corners (radius 0–4px), 2px borders, hard offset shadows (`--shadow-pixel`). Buttons press down 3px on click (`.btn-block`).
- **Spacing:** 8px grid; max content width 1120px; 16px side gutters on mobile.
- **Motion:** 150–250ms ease-out; the irreversible alert shakes once then glows; everything respects `prefers-reduced-motion`.
- **Accessibility:** WCAG AA contrast (parchment on night passes; ink on torch passes). Visible focus rings. All inputs have labels. Charts get an `aria-label` summary and a "view as table" toggle. Status is always text + icon, not colour alone. Keyboard-navigable section cards (`role="radio"` group).
- **Responsive:** test at 360px, 768px and 1280px. No horizontal scroll. Tap targets ≥44px.
- **Empty and loading states:** a skeleton while `today` loads; "Pick a section to start" in the empty state; "Enter at least one subject's attendance to see your plan".

---

## 8. Suggested file structure
```
src/
  app/
    layout.tsx            fonts, header, footer, metadata ("Attendance Predictor · VibeCraft 2026")
    page.tsx              landing
    planner/page.tsx      wraps <Planner/> in <Suspense> (because of useSearchParams)
    timetable/page.tsx
    how-it-works/page.tsx
    globals.css           from kit
  components/
    planner/Planner.tsx   "use client"; reducer, today, localStorage
    planner/SectionPicker.tsx  AttendanceTable.tsx  PlanningDate.tsx
    results/IrreversibleAlert.tsx  StatusBanner.tsx  KpiGrid.tsx  SubjectCard.tsx
    results/SubjectBarChart.tsx  ProjectionChart.tsx  WhatIf.tsx  ThisWeek.tsx  SmartMetrics.tsx
    timetable/WeekGrid.tsx
    ui/StatusChip.tsx  Goal90Badge.tsx  ProgressBar.tsx  PixelButton.tsx  Panel.tsx  NumberInput.tsx
  lib/
    calendar.ts  attendance.ts  useToday.ts   (from kit, unchanged)
    data.ts       typed loader: getSections(), getSection(id)
    format.ts     fmtPct(n|null) -> "84.62%" | "—", fmtCount, pluralize
    storage.ts    safe localStorage get/set
  data/timetables.json
tests/engine.test.ts, tests/python_reference_cases.json
```

---

## 9. Edge cases the judges will try (all must behave)

| # | Case | Expected behaviour |
|---|---|---|
| TC01 | 100% | SAFE; still shows required and safe absences; 90% ACHIEVED |
| TC02–03 | 90.00% vs 89.99% | Exactly 90% counts as reached (≥); 89.99 does not |
| TC04–05 | 75.00% vs 74.99% | 75.00 ≥ 75 → not below; 74.99 is below. Never rounded up |
| TC06 | Below 75%, recoverable | AT RISK, with exact "need X of R, can miss Y" |
| TC07 | Below 75%, impossible | IRREVERSIBLE DETENTION alert with the proof line |
| TC08/TC10 | Planning date = 29 Nov, 0 remaining | Remaining 0; the final state is shown; no division errors |
| TC09 | 1 remaining | Shows whether that one class changes the status |
| TC11 | Date after 29 Nov | Picker blocks it; engine error shown if forced |
| TC12 | Date before today | Picker blocks it; engine error shown if forced |
| TC13 | Weekend planning date | Fine: counts start from the next weekday automatically |
| TC14 | 2-period lab | Counts as 2 (documented on /how-it-works) |
| TC15 | Subject with no classes left | Shows "No classes left: final %" |
| TC16 | Rounding | Engine uses integers; UI rounds to 2 dp only for display |
| TC17 | Invalid inputs | Negative, >100, attended > held, blank, letters: inline error, row excluded, no crash |
| TC18 | Overall | Σ attended ÷ Σ held (`result.overall`) |
| TC19–20 | OCR ambiguity / duplicates | Already resolved in the data; confidence dots on the timetable page |
| extra | Percentage impossible for the held count (e.g. 60% of 16) | Uses the safest lower count and shows the engine's warning |
| extra | Semester already over / not started | Friendly banner, no crash |
| extra | Mobile 360px | Everything usable, no horizontal scroll |

---

## 10. Build order (the event runs on a 9-hour clock — ship a working version early)

**Milestone 1 (≈1.5h), P0 core and deployable**
Scaffold, copy the kit, run the tests (pass 11). Build `/planner` with a plain section select, subject percentage inputs, date picker, and results as plain KPI cards + subject list + irreversible alert. Deploy to Vercel. *At this point it already satisfies the whole problem statement.*

**Milestone 2 (≈2h), P1 correctness UX**
Exact-count toggle, validation messages, planning-gap radio + `otherGap`, percentage-estimate hints, overall status banner, 90% badge, `localStorage`, URL `?section=`. Walk through §9 by hand.

**Milestone 3 (≈2h), P1 differentiators**
Subject bar chart, projection chart, what-if simulator, "This week" list, smart metrics, the `/timetable` page.

**Milestone 4 (≈1.5h), P2 polish**
Landing page, VibeCraft theme everywhere, section cards, animations, responsive pass, accessibility pass, `/how-it-works`, favicon (🧱) and metadata.

**Milestone 5 (≈30m)**
`npm run build` clean, re-run the tests, run the demo script (§11) on the deployed URL, check a phone.

Commit after every milestone. Never leave `main` broken.

---

## 11. Judge demo script (numbers verified with the engine for 28 Sep 2026, section III-ECE-B)

1. **Pick III-ECE-B.** Nine subjects load, and the timetable page shows its real grid.
2. **Discrete Mathematics = 50%** (≈ 8 of 16 held). Result: **AT RISK**. **36** classes left, **need 31**, **can miss 5**, best possible **84.62%**, and the 90% goal is **not reachable**.
3. **Change the planning date to 2 Nov** with "I'll attend everything until then": 16 classes left from 2 Nov, need 11, SAFE. Switch to "I'll miss everything until then": **IRREVERSIBLE DETENTION**, best possible **46.15%**. This shows that the planning date changes everything.
4. **Exact counts for Indian Art Form: attended 0, held 4.** 9 left, max **(0+9)÷(4+9) = 69.23%** < 75%, giving **IRREVERSIBLE DETENTION** with the proof.
5. **Discrete Mathematics = 75%** (12/16): SAFE, need 27 of 36, can miss 9. Then **plan from 29 Nov**: 0 left, final 92.31%, locked.
6. **What-if**: "miss the next 8 Discrete Maths classes" and watch the final % and status change.
7. Open **How it works** and say the thesis line.

> Dates move: on a different day the counts change, because today is read live. Re-check the numbers on the demo morning with the app itself.

---

## 12. Phase 2 readiness (sealed round)
- Keep `lib/` pure and UI-free, so new rules become engine functions plus tests.
- Keep all section and subject data behind `lib/data.ts`, so a new data source replaces one file.
- Keep a `features` config object (e.g. `{ holidays: false, whatIf: true }`) so new capabilities can be toggled.
- Don't add ML now. A roadmap exists (`future_ml.py` in the Python project) if Phase 2 asks for prediction from real attendance history.

---

## 13. Definition of done
- [ ] `npx tsx --test tests/engine.test.ts` → pass 11, fail 0
- [ ] `npm run build` succeeds with no type errors or ESLint errors
- [ ] All 13 sections selectable; every subject shows remaining / need-75 / need-90
- [ ] Today comes from the device, and changing the planning date recomputes everything
- [ ] The "Irreversible Detention" alert appears with a proof line in demo steps 3 and 4
- [ ] No NaN / Infinity / negative / undefined anywhere (try blank and silly inputs)
- [ ] Works at 360px wide; keyboard-usable; reduced motion respected
- [ ] Deployed on Vercel; the demo script works on the live URL

---

## 14. Prompts to paste into Antigravity

**Kickoff (paste first, with this kit folder in the workspace):**
> Read `ANTIGRAVITY_GUIDE.md` fully. We're building the Attendance Predictor for VibeCraft 2026 Round 1 in Next.js. Follow the guide exactly: reuse `lib/attendance.ts`, `lib/calendar.ts`, `lib/useToday.ts`, `data/timetables.json` and `styles/globals.css` unchanged; never reimplement the maths in components; today's date comes only from `useToday()`; fonts come from @fontsource, not next/font/google. Start with §3 setup and Milestone 1 from §10. Run the engine tests and `npm run build` before telling me it's done. Show me the plan first, then build.

**Milestone 2:** "Do Milestone 2 from §10. Then walk through every row of §9 in the running app and report which pass."

**Milestone 3:** "Do Milestone 3 from §10: charts, what-if, This week, smart metrics, /timetable. Use recharts themed with the §7 tokens."

**Milestone 4:** "Do Milestone 4: landing page and full VibeCraft polish per §6.2 and §7. Test at 360, 768 and 1280px and fix any overflow. Check contrast and focus states."

**Final check:** "Run §13's definition of done item by item and fix anything failing. Then run the §11 demo script against the dev server and tell me the actual numbers you see for today's date."

**If something looks wrong in the maths:** "Don't change the engine. Write a failing test in tests/engine.test.ts that shows the problem, and explain it to me first."
