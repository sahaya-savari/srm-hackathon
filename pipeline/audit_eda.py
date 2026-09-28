"""Data-quality audit + EDA over the normalized weekly schedule."""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "data_clean"
sch = pd.read_csv(C / "schedule.csv")
sub = pd.read_csv(C / "subjects.csv")
sec = pd.read_csv(C / "sections.csv")
out = ROOT / "reports"; out.mkdir(exist_ok=True)
issues = []

def add(sid, kind, sev, detail):
    issues.append(dict(section_id=sid, issue=kind, severity=sev, detail=detail))

# ---- 1. contact periods vs L-T-P ------------------------------------------------
cnt = (sch[~sch.slot.str.contains(r"\|")]
       .groupby(["section_id", "subject_code"]).size().rename("weekly_periods").reset_index())
# ambiguous batch-lab periods, split evenly for the check only
amb = sch[sch.slot.str.contains(r"\|")]
codes = sub.groupby(["section_id", "subject_code"]).agg(
    L=("L", "max"), T=("T", "max"), P=("P", "max"), ltpc=("ltpc", "first"),
    subject_name=("subject_name", "first"), slots=("slot", lambda s: ",".join(s))).reset_index()
chk = codes.merge(cnt, how="left", on=["section_id", "subject_code"]).fillna({"weekly_periods": 0})
for _, r in amb.groupby(["section_id", "subject_code"]).size().items():
    pass
amb_share = amb.assign(n=1).groupby(["section_id", "subject_code"]).n.sum()
for (sid, codestr), n in amb_share.items():
    parts = codestr.split("|")
    for c in parts:
        m = (chk.section_id == sid) & (chk.subject_code == c)
        chk.loc[m, "weekly_periods_incl_ambiguous_share"] = chk.loc[m, "weekly_periods"] + n / len(parts)
chk["weekly_periods_incl_ambiguous_share"] = chk["weekly_periods_incl_ambiguous_share"].fillna(chk.weekly_periods)
chk["expected_LTP"] = chk[["L", "T", "P"]].sum(axis=1, min_count=1)
chk["delta"] = chk.weekly_periods_incl_ambiguous_share - chk.expected_LTP
chk.to_csv(out / "contact_hours_vs_ltpc.csv", index=False)
for _, r in chk.iterrows():
    if pd.isna(r.expected_LTP):
        add(r.section_id, "LTPC_MISSING", "medium", f"{r.subject_code} {r.subject_name}: no L-T-P-C printed")
    elif r.delta != 0:
        add(r.section_id, "CONTACT_HOURS_MISMATCH", "medium" if abs(r.delta) <= 1 else "high",
            f"{r.subject_code} ({r.slots}) scheduled {r.weekly_periods_incl_ambiguous_share:g}/wk vs L+T+P={r.expected_LTP:g} ({r.ltpc})")

# ---- 2. listed-but-unscheduled / duplicates in subject table ---------------------
for sid, g in sub.groupby("section_id"):
    used = set("|".join(sch[sch.section_id == sid].slot).split("|"))
    for _, r in g.iterrows():
        if r.slot not in used:
            add(sid, "SUBJECT_NOT_SCHEDULED", "high", f"slot {r.slot} {r.subject_code} listed but never appears in grid")
    d = g[g.subject_code.duplicated(keep=False)]
    if len(d):
        add(sid, "DUPLICATE_CODE_IN_TABLE", "low", f"{d.subject_code.iloc[0]} listed under slots {list(d.slot)} (theory+lab rows)")
    if g.ltpc.eq("MISSING").any():
        pass

# ---- 3. same code, different names across sections; same name different code ----
cur = sub.merge(sec[["section_id", "valid_for_2026_27"]], on="section_id")
cur = cur[cur.valid_for_2026_27]
for code, g in cur.groupby("subject_code"):
    names = set(g.subject_name.str.lower().str.replace(r"[^a-z]", "", regex=True))
    if len(names) > 1:
        add("*", "NAME_VARIANT", "low", f"{code}: {sorted(set(g.subject_name))}")
    if g.ltpc.nunique() > 1:
        add("*", "LTPC_VARIANT", "medium", f"{code}: {sorted(set(g.ltpc))}")
for name, g in cur.groupby(cur.subject_name.str.lower()):
    if g.subject_code.nunique() > 1:
        add("*", "CODE_VARIANT", "medium", f"'{name}' has codes {sorted(set(g.subject_code))} in {sorted(set(g.section_id))}")

# ---- 4. faculty spelling variants ------------------------------------------------
def fkey(f):
    f = re.sub(r"(Dr|Mrs|Ms|Mr)\.?", "", str(f), flags=re.I)
    return re.sub(r"[^a-z]", "", f.lower())
fac = cur[["section_id", "faculty"]].copy()
fac["faculty"] = fac.faculty.str.split(r"\s*[/&;]\s*")
fac = fac.explode("faculty")
fac["key"] = fac.faculty.map(fkey)
variants = [("anand", "annand"), ("prasannavenkatesh", "prasanavenkatesh"), ("prasannavenkatesh", "prassannavenkatesh"),
            ("vinothraj", "rvinothraj")]
seen = set(fac.faculty.dropna())
for f in sorted(seen):
    if "Dr. Dr." in f:
        add("III-ECE-DS", "FACULTY_NAME_TYPO", "low", f"'{f}' (duplicated title)")
groups = {}
for f in seen:
    k = fkey(f)
    k2 = re.sub(r"^(?:[a-z]{1,2})(?=[a-z]{4,})", "", k)  # drop initials
    groups.setdefault(k2[-8:], set()).add(f)
for k, v in groups.items():
    if len(v) > 1:
        add("*", "FACULTY_NAME_VARIANT", "low", f"possible same person: {sorted(v)}")

# ---- 5. cross-section faculty double-booking (2026-27 only) ------------------------
theory = sch[sch.valid_for_2026_27 & ~sch.slot.str.contains(r"\|")].merge(
    sub[["section_id", "slot", "faculty"]], on=["section_id", "slot"], how="left")
theory = theory[~theory.faculty.str.contains("CDC", na=False)]
theory["fac_list"] = theory.faculty.str.split(r"\s*[/&;]\s*")
ex = theory.explode("fac_list")
ex["fk"] = ex.fac_list.map(fkey)  # strict key: initials kept, so M.Manikandan != V.Manikandan
ex = ex[(ex.fk.str.len() > 4) & ~ex.fk.str.startswith("newfaculty")]  # placeholders are not people
for (fk, d, p), g in ex.groupby(["fk", "day_of_week", "period"]):
    if g.section_id.nunique() > 1 and not (g.class_type == "lab").all():
        add(",".join(sorted(g.section_id.unique())), "FACULTY_CLASH", "info",
            f"{g.fac_list.iloc[0]} scheduled in {sorted(g.section_id.unique())} at {d} P{p} "
            f"({sorted(set(g.subject_code))}) — may be a combined/shared class")

# ---- 6. structural / header issues found during visual inspection -----------------
for _, s in sec.iterrows():
    if not s.valid_for_2026_27:
        add(s.section_id, "STALE_TIMETABLE", "critical",
            f"page {s.page} of '{s.source_file}' is academic year {s.academic_year} (semester_type='{s.semester_type}'); "
            "not valid for the 29-Aug-2026..29-Nov-2026 semester")
add("I-ECE-*", "FILE_SECTION_MISMATCH", "high",
    "'I year Time Table SEEE.pdf' holds 4 section timetables (I ECE-A; I ECE-B+EEE; I ECE-DS; I Biotech-B+BME), not one")
add("I-ECE-DS,I-BIOTECH-B-BME", "HEADER_CONTRADICTION", "high", "header says 'EVEN SEMESTER (2024-25)' but body says Year/Sem I/I")
add("I-*", "DIFFERENT_BELL_SCHEDULE", "high", "I-year grid uses 9.55/10.50/11.45/12.35 bells and no fixed lunch; 2026-27 grids use 9.50/10.50/11.40/12.30 with lunch in P5")
add("I-ECE-B-EEE,I-ECE-DS", "CLASS_IN_LUNCH_PERIOD", "medium", "classes placed in period 5 (12.35-1.30), e.g. 'PPS LAB IST618', 'German'")
add("I-*", "HANDWRITTEN_EDITS", "medium", f"{int(sch.handwritten.sum())} period-cells come from handwritten annotations (room numbers, labs, NSS)")
add("I-ECE-DS", "FADED_CELL", "medium", "Fri P4 'PPS LAB' printed faded/grey — possibly withdrawn; kept but flagged")
add("III-ECE-A,III-ECE-DS,II-ECE-DS-B", "PLACEHOLDER_FACULTY", "low", "Maths faculty listed as 'New Faculty 2/3' (not yet assigned)")
add("I-BIOTECH-B-BME", "MISSING_FACULTY", "low", "slot G 21BTB104T has no faculty / designation")
add("I-*", "SLOT_LETTERS_NOT_STABLE", "high", "slot letter meaning changes between I-year pages (C = PCB Design on p1/p3, Biology on p2, Cell Biology on p4)")
add("IV-ECE-B", "HEADER_TYPO", "low", "period-1 time printed '09.000 / 9.50'")
add("IV-ECE-A,IV-ECE-B", "LAB_WITHOUT_P_CREDIT", "medium", "21ECC402P has a LAB row and a 1-period lab/week but L-T-P-C = 2-1-0-3 (P=0)")
add("II-BME", "AMBIGUOUS_BATCH_LAB", "high", "'DLMS/EEC' 2x2-period labs: per-student course mapping for each day is UNKNOWN (batch rotation)")
add("III-ECE-*", "PROJECT_HOUR_LABEL", "medium", "'B-Proj' cell interpreted as slot-B project hour (needs confirmation)")
add("III-BME", "LAB_LABEL_NOT_SLOT", "medium", "'MPMC LAB' / 'BIO DSP LAB' mapped to slots B / C by name")
add("ALL", "SATURDAY_UNSPECIFIED", "high", "Semester spans 29-Aug (Sat) to 29-Nov (Sun); grids cover Mon-Fri only. Saturday instruction / day-order working days are UNKNOWN")
add("ALL", "NO_HOLIDAY_CALENDAR", "critical", "No academic calendar, holidays, exam weeks or cancellations supplied — only scheduled occurrences can be modelled")

iss = pd.DataFrame(issues).drop_duplicates()
iss.to_csv(out / "data_quality_issues.csv", index=False)

# ---- per-file DQ summary ----------------------------------------------------------
ocr = pd.read_csv(C / "ocr_crosscheck.csv")
summ = []
for _, s in sec.iterrows():
    g = sch[sch.section_id == s.section_id]
    n_iss = iss[iss.section_id.str.contains(s.section_id.split("-")[0] + r"\b|\*|ALL", regex=True)
                | iss.section_id.str.contains(s.section_id, regex=False)]
    o = ocr[ocr.section_id == s.section_id].iloc[0]
    low = int((g.mapping_confidence == "low").sum()); med = int((g.mapping_confidence == "medium").sum())
    summ.append(dict(file=s.source_file, page=s.page, section=s.section_id, pages_in_file=4 if "I year" in s.source_file else 1,
                     period_rows=len(g), rows_visually_verified=int(g.visual_verified.sum()),
                     raw_ocr_code_recall=o.code_recall_exact, ocr_mean_word_conf=o.ocr_mean_word_conf,
                     handwritten_cells=int(g.handwritten.sum()), low_conf_mappings=low, medium_conf_mappings=med,
                     empty_slots=5 * 8 - g[g.period != 5][["day_of_week", "period"]].drop_duplicates().shape[0],
                     duplicates=0, conflicts=low,
                     confidence="LOW" if not s.valid_for_2026_27 else ("MEDIUM" if low else ("HIGH-" if med else "HIGH")),
                     status=s.status))
summ = pd.DataFrame(summ)
summ.to_csv(out / "data_quality_summary.csv", index=False)

# ---- EDA (2026-27 sections only) ------------------------------------------------
cs = sch[sch.valid_for_2026_27]
per_sec = cs.groupby("section_id").agg(
    weekly_periods=("period", "size"),
    lab_periods=("is_lab", "sum"),
    subjects=("subject_code", lambda s: len(set("|".join(s).split("|")))),
    first_period=("period", "min"), last_period=("period", "max"))
per_sec["lab_share"] = (per_sec.lab_periods / per_sec.weekly_periods).round(2)
fn = cs[cs.period <= 4].groupby("section_id").size(); an = cs[cs.period >= 6].groupby("section_id").size()
per_sec["forenoon_periods"] = fn; per_sec["afternoon_periods"] = an.reindex(per_sec.index).fillna(0).astype(int)
per_sec["venue_shift_label"] = sec.set_index("section_id").home_venue.reindex(per_sec.index).str.extract(r"(FN|AN)$")[0].fillna("-")
byday = cs.pivot_table(index="section_id", columns="day_of_week", values="period", aggfunc="size").fillna(0).astype(int)
byday = byday[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]]
per_sec = per_sec.join(byday)
per_sec["busiest_day"] = byday.idxmax(axis=1); per_sec["lightest_day"] = byday.idxmin(axis=1)
per_sec["max_day_load"] = byday.max(axis=1); per_sec["min_day_load"] = byday.min(axis=1)
per_sec["avg_per_day"] = (per_sec.weekly_periods / 5).round(1)
per_sec["semester_scheduled_periods"] = per_sec.weekly_periods * 13
per_sec.to_csv(out / "eda_sections.csv")
byperiod = cs.groupby("period").size()
ctype = cs.groupby(["section_id", "class_type"]).size().unstack(fill_value=0)
ctype.to_csv(out / "eda_class_types.csv")
freq = cs.groupby(["section_id", "subject_code", "subject_name"]).size().rename("per_week").reset_index()
freq.to_csv(out / "eda_subject_frequency.csv", index=False)

pd.set_option("display.width", 250)
print(per_sec.to_string()); print(byperiod.to_string()); print(ctype.to_string())
print(freq.per_week.value_counts().sort_index().to_string())
print(iss.groupby(["issue", "severity"]).size().to_string())
print(summ.to_string())
print(chk[chk.delta != 0][["section_id", "subject_code", "slots", "ltpc", "weekly_periods_incl_ambiguous_share", "expected_LTP", "delta"]].to_string())
print(iss[iss.issue.isin(["FACULTY_CLASH", "NAME_VARIANT", "CODE_VARIANT", "LTPC_VARIANT", "FACULTY_NAME_VARIANT", "SUBJECT_NOT_SCHEDULED"])].to_string())
