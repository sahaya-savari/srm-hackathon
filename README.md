# Attendance Predictor — VibeCraft 2026 (Round 1: The Overworld)

> **Event:** VibeCraft 2026 (Neuro Tech Titans × YUVA'26, SRM IST Tiruchirappalli)  
> **Challenge:** Smart Attendance Dashboard & Decision Engine (Semester: 29 Aug 2026 → 29 Nov 2026)

A decision engine that eliminates guesswork by calculating precisely how many classes a student must attend to stay above **75%** (detention threshold) or reach **90%**, with instant mathematical proofs for **Irreversible Detention** before detention becomes mathematically unavoidable.

---

## 📁 Repository Layout

```
attendance_predictor/
├── web/                   # Next.js 16 App Router frontend (TypeScript, Tailwind v4)
│   ├── src/app/           # Routes: /, /planner, /timetable, /how-it-works
│   ├── src/components/    # Planner, Timetable, KPI grids, status badges
│   ├── src/lib/           # TypeScript deterministic attendance engine, calendar, useToday
│   ├── src/data/          # timetables.json (13 verified class sections)
│   └── tests/             # 11 tests (including 3,658 reference cross-checks)
├── engine/                # Core Python deterministic calculation engines
│   ├── attendance_engine.py  # Integer math, status classifications, trajectory, plan() API
│   └── calendar_engine.py    # Semester calendar, scheduled occurrences, slot resolution
├── data_clean/            # Normalized CSV timetables, schedules, subject catalogues
├── data_raw/              # Verbatim transcription and raw scans of the 10 PDF pages
├── pipeline/              # Data ingestion, normalization, and OCR cross-check pipelines
├── reports/               # Data quality audit, contact hours, and EDA reports
├── tests/                 # Python unit test suite (tests/test_engine.py — 24 tests)
├── app.py                 # Streamlit interactive desktop prototype
└── requirements.txt       # Python dependencies
```

---

## 🚀 Running the Web Application (Next.js)

The modern client-side frontend is located in `web/`.

```bash
# 1. Navigate to the web frontend directory
cd web

# 2. Install dependencies
npm install

# 3. Launch local development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser:
- **`/`** — Landing page with live semester stats strip and feature explainer.
- **`/planner`** — Core Decision Engine: section selector, quick-percentage & exact-count inputs, lookahead planning date picker with gap policy ("attend all" vs "miss all"), 6 KPI answers, and subject breakdown.
- **`/timetable`** — Weekly period-by-period timetable grid (Mon–Fri) and semester occurrence audit for each section.
- **`/how-it-works`** — Transparent technical methodology, integer arithmetic proofs, and data provenance.

### Production Build & Linting

```bash
cd web
npm run lint      # Runs ESLint (0 errors, 0 warnings)
npm run build     # Compiles production Next.js build with Turbopack
```

---

## 🧪 Running the Tests

### 1. TypeScript Engine Test Suite (Frontend)
Runs with Node's native test runner via `tsx`:
```bash
cd web
npx tsx --test tests/engine.test.ts
```
*Result:* **11 passed, 0 failed** (includes 3,658 per-subject parity cross-checks against the Python reference engine across 400 random student plans).

### 2. Python Engine Test Suite
```bash
python -m pytest -q tests
```
*Result:* **24 passed in ~3.0s**.

---

## 🐍 Running the Streamlit Prototype (Python)

```bash
pip install -r requirements.txt streamlit plotly
streamlit run app.py
```
Runs at [http://localhost:8501](http://localhost:8501).

---

## 📐 Key Assumptions & Counting Rules

1. **Counting Unit**: 1 timetable period = 1 attendance hour. A 2-period lab block counts as 2 discrete attendance hours.
2. **Instruction Days**: Monday through Friday only. Saturdays and Sundays are non-instructional.
3. **Scheduled vs Conducted**: Class counts reflect scheduled occurrences from the timetable. Classes before today are counted as held; classes from the planning date forward are counted as remaining.
4. **Hydration-Safe Device Clock**: Today's date is dynamically read from the student's browser via `useToday()`, never hardcoded or pre-rendered at build time.
5. **Exact Integer Arithmetic**: To eliminate IEEE-754 floating-point drift (e.g. `0.55 * 100 = 55.00000000000001`), all threshold comparisons use exact integer cross-multiplication:
   $$\frac{\text{attended}}{\text{held}} \ge \frac{p}{q} \iff q \times \text{attended} \ge p \times \text{held}$$
6. **Conservative Estimation**: In percentage mode, the engine resolves rounding ambiguities by choosing the lowest consistent attended count, ensuring students never receive over-optimistic safety margins.
7. **All 13 Sections Supported**: Includes the 9 active 2026-27 sections plus the 4 first-year 2024-25 sections (clearly flagged with an archival badge).
8. **Mathematical Irreversible Proof**: When recovery to 75% is mathematically impossible, the dashboard displays:
   $$\frac{A + R}{H + R} < 75.00\%$$

---

## ☁️ Deployment

- **Frontend (Vercel)**:
  - **Framework Preset**: Next.js
  - **Root Directory**: `web`
  - **Build Command**: `next build`
  - **Output Directory**: `.next`
