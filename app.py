"""
Attendance Predictor — Streamlit UI
VIBECRAFT 2026, Round 1: The Overworld — Phase 1 Core Calculator

This file is UI ONLY. Every formula lives in engine/calendar_engine.py and
engine/attendance_engine.py (pure functions, unit-tested — see tests/). The UI
reads today's date dynamically (date.today()); it is never hardcoded.

Run with:  streamlit run app.py
"""
import sys
import os
import random
from datetime import date, timedelta
from fractions import Fraction

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine"))
from calendar_engine import (CalendarConfig, sections as list_sections, weekly_template,
                              count_by_subject, SEMESTER_START, SEMESTER_END, DISCLAIMER)
from attendance_engine import (SubjectInput, plan, required_classes, max_possible, min_possible,
                                detention_status, goal90_status, immediate_skip_budget,
                                CHALLENGE_LABEL_75, T75, T90)

TODAY = date.today()  # dynamic — never hardcoded

# --------------------------------------------------------------------------- page setup
st.set_page_config(page_title="Attendance Predictor", page_icon="🎓", layout="wide")

STATUS_COLOR = {
    "SAFE": "#1e8e5a", "LOCKED_SAFE": "#1e8e5a",
    "RECOVERING": "#b8860b", "CRITICAL": "#b8860b",
    "IRREVERSIBLE": "#c0392b", "NO_DATA": "#6b7280",
    "ACHIEVED": "#1e8e5a", "LOCKED": "#1e8e5a", "RECOVERABLE": "#b8860b", "IMPOSSIBLE": "#c0392b",
}

st.markdown("""
<style>
.block-container {padding-top: 1.6rem; max-width: 1180px;}
.ap-title {font-size: 2.1rem; font-weight: 800; margin-bottom: 0;}
.ap-subtitle {color: #6b7280; font-size: 1.02rem; margin-top: 0.1rem; margin-bottom: 1.2rem;}
.kpi-card {background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px 16px;
           box-shadow: 0 1px 2px rgba(0,0,0,0.04); height: 100%;}
.kpi-label {font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.03em; font-weight: 600;}
.kpi-value {font-size: 1.65rem; font-weight: 800; margin-top: 2px; color: #111827;}
.kpi-sub {font-size: 0.78rem; color: #9ca3af; margin-top: 2px;}
.status-banner {border-radius: 12px; padding: 18px 20px; font-weight: 700; font-size: 1.05rem; margin-bottom: 0.6rem;}
.status-safe {background: #eafaf1; border: 1px solid #1e8e5a; color: #14532d;}
.status-risk {background: #fff8e6; border: 1px solid #b8860b; color: #7a5b00;}
.status-irrev {background: #fdecea; border: 1px solid #c0392b; color: #7f1d1d;}
.goal-badge {display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; color: white;}
.plain-metric {padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-size: 0.95rem;}
.disclaimer {font-size: 0.82rem; color: #6b7280; border-top: 1px solid #e5e7eb; margin-top: 1.5rem; padding-top: 0.8rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ap-title">Attendance Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="ap-subtitle">Timetable-aware attendance planning &amp; detention risk analysis</div>',
            unsafe_allow_html=True)


# --------------------------------------------------------------------------- helpers
@st.cache_data
def section_subject_table(section_id: str) -> pd.DataFrame:
    """One row per unique subject_code actually in the timetable (LAB rows already
    folded into their theory code upstream in the pipeline; batch-shared labs keep
    their own combined code, e.g. '21BMC203J|21BMC204J')."""
    tpl = weekly_template(section_id)
    g = tpl.groupby("subject_code").agg(subject_name=("subject_name", "first"),
                                         weekly_frequency=("period", "size")).reset_index()
    return g.sort_values("weekly_frequency", ascending=False).reset_index(drop=True)


def held_so_far(section_id: str, subject_code: str, today: date) -> int:
    return count_by_subject(section_id, SEMESTER_START, today - timedelta(days=1)).get(subject_code, 0)


def demo_attendance(section_id: str, today: date) -> dict:
    """Deterministic demo data so the app looks populated immediately, and always
    contrasts a SAFE, a RECOVERABLE and (when the timetable allows it) an
    IRREVERSIBLE subject — per the judge-demo guidance ('don't demo only the easy
    case'). Seeded on section_id + today so it's stable within a day, but moves
    as the semester progresses."""
    rng = random.Random(f"{section_id}:{today.isoformat()}")
    subs = section_subject_table(section_id)
    out = {}
    # lowest-frequency subject deliberately pushed to 0 attended -> most likely
    # to be mathematically irreversible early in the semester (see report).
    lowest_freq_code = subs.iloc[-1].subject_code if len(subs) else None
    for i, row in subs.iterrows():
        H = held_so_far(section_id, row.subject_code, today)
        if row.subject_code == lowest_freq_code:
            A = 0
        elif i % 3 == 1:
            A = round(H * rng.uniform(0.50, 0.66))          # deliberately borderline/recoverable
        else:
            A = round(H * rng.uniform(0.82, 1.0))            # comfortably safe
        out[row.subject_code] = (min(A, H), H)
    return out


def fmt_pct(x):
    return "—" if x is None else f"{x:.2f}%"


def kpi(col, label, value, sub=""):
    with col:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                     f'<div class="kpi-value">{value}</div>'
                     f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)


def overall_from_records(records):
    """Overall = totals, per TC18 (Σattended/Σheld, never an average of %s),
    recomputed with the SAME exact-fraction engine functions as any subject."""
    tot_A = sum(r["classesAttendedAtPlanningDate"] for r in records)
    tot_H = sum(r["classesHeldAtPlanningDate"] for r in records)
    tot_n = sum(r["classesRemaining"] for r in records)
    x75 = required_classes(tot_A, tot_H, tot_n, T75) if tot_H + tot_n else 0
    x90 = required_classes(tot_A, tot_H, tot_n, T90) if tot_H + tot_n else 0
    f75, f90 = x75 <= tot_n, x90 <= tot_n
    st75 = detention_status(tot_A, tot_H, tot_n, T75) if tot_H + tot_n else "NO_DATA"
    st90 = goal90_status(tot_A, tot_H, tot_n) if tot_H + tot_n else "NO_DATA"
    mx = max_possible(tot_A, tot_H, tot_n) if tot_H + tot_n else None
    mn = min_possible(tot_A, tot_H, tot_n) if tot_H + tot_n else None
    return dict(subject="OVERALL", subjectName="Overall (all subjects, weighted by class counts)",
                currentAttendance=round(tot_A / tot_H * 100, 2) if tot_H else None,
                classesAttendedAtPlanningDate=tot_A, classesHeldAtPlanningDate=tot_H,
                attendanceAtPlanningDate=round(tot_A / tot_H * 100, 2) if tot_H else None,
                classesRemaining=tot_n,
                requiredTo75=x75 if f75 else None, requiredTo90=x90 if f90 else None,
                safeAbsences=(tot_n - x75) if f75 else None,
                maximumPossibleAttendance=round(float(mx) * 100, 2) if mx is not None else None,
                minimumPossibleAttendance=round(float(mn) * 100, 2) if mn is not None else None,
                requiredAttendanceRate75=round(x75 / tot_n, 3) if tot_n and f75 else None,
                detentionStatus=st75, recoveryStatus75=CHALLENGE_LABEL_75.get(st75, st75), recoveryStatus90=st90,
                explanation75=(f"Overall: even attending every one of the {tot_n} remaining classes across all "
                               f"subjects only reaches {round(float(mx)*100,2) if mx is not None else '?'}%, "
                               f"below the 75% minimum." if st75 == "IRREVERSIBLE" else
                               (f"Overall: you are safe even if every remaining class is missed."
                                if st75 == "LOCKED_SAFE" else
                                f"Overall: attend at least {x75} of the {tot_n} remaining classes across all "
                                f"subjects to stay at or above 75%.")))


# --------------------------------------------------------------------------- top controls
sections_available = list_sections()
c1, c2, c3 = st.columns([1.4, 1, 1])
with c1:
    section_id = st.selectbox("Section", sections_available, index=0)
with c2:
    input_mode = st.radio("Attendance input", ["Exact (attended / held)", "Percentage (quick, estimated)"],
                           horizontal=False)
with c3:
    planning_date = st.date_input("Planning date", value=TODAY, min_value=SEMESTER_START, max_value=SEMESTER_END)

subs_df = section_subject_table(section_id)

# gap assumption — only matters when planning_date > today
gap_policy = "best"
if planning_date > TODAY:
    gap_choice = st.radio(
        f"Between today ({TODAY.isoformat()}) and the planning date, assume the classes not yet held will be:",
        ["Attended (optimistic)", "Missed (worst case)"], horizontal=True,
        help="You entered attendance as of today. Classes between today and the planning date haven't "
             "happened yet, so the engine shows both scenarios; pick which one drives the main numbers.")
    gap_policy = "best" if gap_choice.startswith("Attended") else "worst"

# planning-date validity — mirrors the deterministic engine's own checks (TC10-12)
if planning_date < TODAY:
    st.error("Planning date is before today. Historical planning isn't supported — pick today or a future date.")
    st.stop()
if planning_date > SEMESTER_END:
    st.error(f"Planning date is after the semester end ({SEMESTER_END.isoformat()}). Pick a date on or before it.")
    st.stop()

st.markdown("#### Subject attendance")
demo = demo_attendance(section_id, TODAY)

if input_mode.startswith("Exact"):
    editor_df = pd.DataFrame([
        {"Subject": f"{r.subject_name} ({r.subject_code})", "subject_code": r.subject_code,
         "Weekly freq": r.weekly_frequency, "Attended": demo[r.subject_code][0], "Held": demo[r.subject_code][1]}
        for r in subs_df.itertuples()
    ])
    edited = st.data_editor(
        editor_df, hide_index=True, use_container_width=True, key=f"editor_{section_id}",
        column_config={
            "subject_code": None,
            "Subject": st.column_config.TextColumn(disabled=True),
            "Weekly freq": st.column_config.NumberColumn(disabled=True, help="Periods/week from the timetable"),
            "Attended": st.column_config.NumberColumn(min_value=0, step=1),
            "Held": st.column_config.NumberColumn(min_value=0, step=1),
        })
    subject_inputs, warnings_ui = [], []
    for _, row in edited.iterrows():
        A, H = int(row["Attended"]), int(row["Held"])
        if A < 0 or H < 0:
            warnings_ui.append(f"'{row['Subject']}': negative values are invalid — clamped to 0.")
            A, H = max(A, 0), max(H, 0)
        if A > H:
            warnings_ui.append(f"'{row['Subject']}': attended ({A}) > held ({H}) is invalid — clamped to {H}.")
            A = H
        subject_inputs.append(SubjectInput(row["subject_code"], attended=A, held=H))
else:
    editor_df = pd.DataFrame([
        {"Subject": f"{r.subject_name} ({r.subject_code})", "subject_code": r.subject_code,
         "Weekly freq": r.weekly_frequency,
         "Attendance %": round(demo[r.subject_code][0] / demo[r.subject_code][1] * 100, 0) if demo[r.subject_code][1] else 0}
        for r in subs_df.itertuples()
    ])
    edited = st.data_editor(
        editor_df, hide_index=True, use_container_width=True, key=f"editor_pct_{section_id}",
        column_config={
            "subject_code": None,
            "Subject": st.column_config.TextColumn(disabled=True),
            "Weekly freq": st.column_config.NumberColumn(disabled=True),
            "Attendance %": st.column_config.NumberColumn(min_value=0, max_value=100, step=1),
        })
    subject_inputs, warnings_ui = [], []
    for _, row in edited.iterrows():
        p = float(row["Attendance %"])
        if not (0 <= p <= 100):
            warnings_ui.append(f"'{row['Subject']}': {p}% is out of range — clamped to [0, 100].")
            p = min(max(p, 0), 100)
        subject_inputs.append(SubjectInput(row["subject_code"], percent=p))

# --------------------------------------------------------------------------- run the engine
result = plan(section_id, subject_inputs, today=TODAY, planning_date=planning_date, gap_policy=gap_policy)

if "error" in result:
    for e in result["error"]:
        st.error(e)
    st.stop()

for w in warnings_ui:
    st.warning(w)
for w in result.get("warnings", []):
    st.info(w)

records = result["subjects"]
records_by_code = {r["subject"]: r for r in records}
overall = overall_from_records(records)

focus_options = ["Overall (all subjects)"] + [f'{r["subjectName"]} ({r["subject"]})' for r in records]
focus_choice = st.selectbox("Focus subject (drives the cards and charts below)", focus_options)
focus = overall if focus_choice.startswith("Overall") else records_by_code[focus_choice.split("(")[-1].rstrip(")")]

st.divider()

# --------------------------------------------------------------------------- status banner
status75 = focus["detentionStatus"]
if status75 == "IRREVERSIBLE":
    st.markdown(f'<div class="status-banner status-irrev">🚨 IRREVERSIBLE DETENTION — {focus["subjectName"]}<br>'
                f'<span style="font-weight:500;">{focus["explanation75"]}</span></div>', unsafe_allow_html=True)
elif status75 in ("RECOVERING", "CRITICAL"):
    st.markdown(f'<div class="status-banner status-risk">⚠️ AT RISK — {focus["subjectName"]}<br>'
                f'<span style="font-weight:500;">{focus["explanation75"]}</span></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="status-banner status-safe">✅ SAFE — {focus["subjectName"]}<br>'
                f'<span style="font-weight:500;">{focus["explanation75"]}</span></div>', unsafe_allow_html=True)

goal90 = focus["recoveryStatus90"]
st.markdown(f'90% goal: <span class="goal-badge" style="background:{STATUS_COLOR.get(goal90,"#6b7280")}">'
            f'{goal90}</span>', unsafe_allow_html=True)
st.write("")

# --------------------------------------------------------------------------- KPI cards
cols = st.columns(6)
kpi(cols[0], "Current attendance", fmt_pct(focus["currentAttendance"]), "as of today, Σattended/Σheld" if focus["subject"] == "OVERALL" else "attended / held so far")
kpi(cols[1], "Remaining classes", focus["classesRemaining"], f"{planning_date.isoformat()} → {SEMESTER_END.isoformat()}")
kpi(cols[2], "Required for 75%", focus["requiredTo75"] if focus["requiredTo75"] is not None else "Not possible",
    "of the remaining classes")
kpi(cols[3], "Required for 90%", focus["requiredTo90"] if focus["requiredTo90"] is not None else "Not achievable",
    "of the remaining classes")
kpi(cols[4], "Maximum recoverable", fmt_pct(focus["maximumPossibleAttendance"]), "if every remaining class is attended")
rb = round(focus["requiredAttendanceRate75"] * 100, 1) if focus.get("requiredAttendanceRate75") is not None else None
kpi(cols[5], "Recovery burden", f"{rb}%" if rb is not None else "—", "required-to-75 ÷ remaining classes")

st.write("")

# --------------------------------------------------------------------------- charts
chart_cols = st.columns([1, 1])

with chart_cols[0]:
    st.markdown("**Current vs Target Attendance**")
    cur = focus["currentAttendance"] or 0
    fig1 = go.Figure(go.Bar(
        x=[cur, 75, 90], y=["Current", "75% target", "90% target"], orientation="h",
        marker_color=[STATUS_COLOR.get(status75, "#6b7280"), "#b8b8b8", "#8a8a8a"],
        text=[f"{cur:.1f}%", "75%", "90%"], textposition="outside"))
    fig1.update_layout(xaxis=dict(range=[0, 105], title="Attendance %"), height=280,
                        margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with chart_cols[1]:
    st.markdown("**Subject-wise Attendance**")
    sub_rows = sorted(records, key=lambda r: r["currentAttendance"] or 0)
    colors = [STATUS_COLOR.get(r["detentionStatus"], "#6b7280") for r in sub_rows]
    fig2 = go.Figure(go.Bar(
        x=[r["currentAttendance"] or 0 for r in sub_rows],
        y=[r["subject"] for r in sub_rows], orientation="h", marker_color=colors,
        text=[fmt_pct(r["currentAttendance"]) for r in sub_rows], textposition="outside"))
    fig2.add_vline(x=75, line_dash="dash", line_color="#b8860b")
    fig2.add_vline(x=90, line_dash="dash", line_color="#1e8e5a")
    fig2.update_layout(xaxis=dict(range=[0, 105], title="Attendance %"), height=280,
                        margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("**Attendance Projection** — from the planning date to semester end")
if focus["subject"] == "OVERALL":
    A_eff, H_eff, n = overall["classesAttendedAtPlanningDate"], overall["classesHeldAtPlanningDate"], overall["classesRemaining"]
else:
    A_eff = focus["classesAttendedAtPlanningDate"]
    H_eff = focus["classesHeldAtPlanningDate"]
    n = focus["classesRemaining"]
ks = list(range(n + 1))
best = [(A_eff + k) / (H_eff + k) * 100 if (H_eff + k) else 0 for k in ks]
worst = [A_eff / (H_eff + k) * 100 if (H_eff + k) else 0 for k in ks]
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=ks, y=best, mode="lines", name="Attend all remaining", line=dict(color="#1e8e5a", width=3)))
fig3.add_trace(go.Scatter(x=ks, y=worst, mode="lines", name="Attend none remaining", line=dict(color="#c0392b", width=3)))
fig3.add_hline(y=75, line_dash="dash", line_color="#b8860b", annotation_text="75%")
fig3.add_hline(y=90, line_dash="dash", line_color="#1e8e5a", annotation_text="90%")
fig3.update_layout(xaxis_title="Remaining classes attended so far in this projection",
                    yaxis_title="Attendance %", yaxis=dict(range=[0, 105]), height=320,
                    margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------- planning simulator
st.markdown("### 📅 Plan Your Attendance")
p1, p2, p3, p4 = st.columns(4)
with p1:
    st.metric("Planning date", planning_date.isoformat())
with p2:
    gap_n = 0 if focus["subject"] == "OVERALL" else focus["classesBetweenTodayAndPlanningDate"]
    st.metric("Classes until planning date", gap_n if planning_date > TODAY else 0,
              help="Classes between today and the planning date; not yet held, so the engine applies your "
                   "chosen assumption above.")
with p3:
    st.metric("Required to stay ≥ 75%", focus["requiredTo75"] if focus["requiredTo75"] is not None else "N/A")
with p4:
    st.metric("Projected attendance (attend all)", f"{best[-1]:.2f}%" if ks else "—")

st.divider()

# --------------------------------------------------------------------------- smart metrics (plain language)
st.markdown("### 🧭 Smart Metrics")
m1, m2 = st.columns(2)
buffer_pp = round((focus["currentAttendance"] or 0) - 75, 1)
with m1:
    st.markdown(f'<div class="plain-metric"><b>Attendance buffer:</b> you are '
                f'{abs(buffer_pp)} points {"above" if buffer_pp >= 0 else "below"} the 75% line.</div>',
                unsafe_allow_html=True)
    safe_txt = (f"{focus['safeAbsences']} classes" if focus.get("safeAbsences") is not None else "none — recovery is not mathematically possible")
    st.markdown(f'<div class="plain-metric"><b>Safe absences remaining:</b> {safe_txt}.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="plain-metric"><b>Recovery burden:</b> '
                f'{f"you must attend {rb}% of your remaining classes to stay safe." if rb is not None else "not applicable — see status above."}</div>',
                unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="plain-metric"><b>Maximum recoverable attendance:</b> '
                f'{fmt_pct(focus["maximumPossibleAttendance"])} if every remaining class is attended.</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="plain-metric"><b>75% recovery status:</b> {focus["recoveryStatus75"]}.</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="plain-metric"><b>90% goal:</b> {goal90}.</div>', unsafe_allow_html=True)

if focus["subject"] != "OVERALL":
    st.markdown("##### Subject risk concentration (least headroom first)")
    risk_tbl = pd.DataFrame([{
        "Subject": r["subjectName"], "Current %": r["currentAttendance"],
        "Safe absences": r["safeAbsences"] if r["safeAbsences"] is not None else "—",
        "Status": r["recoveryStatus75"],
    } for r in sorted(records, key=lambda r: (r["safeAbsences"] if r["safeAbsences"] is not None else -1))])
    st.dataframe(risk_tbl, hide_index=True, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------- what-if simulator
st.markdown("### 🔮 What-If Simulator")
st.caption("Test a scenario without changing your saved attendance above. Exact counts are used internally; "
           "percentage-mode subjects are labelled as estimates.")
max_missable = max(0, n)
miss_n = st.slider("What if I miss this many of my NEXT scheduled classes (this subject/overall)?",
                    0, min(max_missable, 12) if max_missable else 0, 0)
if max_missable == 0:
    st.info("No remaining classes to simulate for this selection.")
else:
    A_after_miss = A_eff
    H_after_miss = H_eff + miss_n
    remaining_after = n - miss_n
    proj_final_if_rest_attended = (A_after_miss + remaining_after) / (H_after_miss + remaining_after) * 100 if (H_after_miss + remaining_after) else 0
    still_recoverable = proj_final_if_rest_attended >= 75
    w1, w2, w3 = st.columns(3)
    w1.metric(f"After missing {miss_n} more", f"{A_after_miss}/{H_after_miss}")
    w2.metric("Best possible if you attend the rest", f"{proj_final_if_rest_attended:.2f}%")
    w3.metric("Still ≥ 75% achievable?", "Yes" if still_recoverable else "No")
    if not still_recoverable and miss_n > 0:
        st.warning(f"Missing {miss_n} more classes would make 75% mathematically unreachable for this selection.")

st.divider()
with st.expander("✅ Built-in sanity check (spec test cases)"):
    st.caption("These are the three worked examples from the challenge spec, computed live by the same "
               "engine functions used above — not hardcoded outputs.")
    check_rows = []
    for A, H, R in [(80, 100, 20), (60, 100, 40), (70, 100, 50)]:
        mx = float(max_possible(A, H, R)) * 100
        st_ = detention_status(A, H, R, T75)
        check_rows.append({"A": A, "H": H, "R": R, "Current %": round(A / H * 100, 2),
                            "Max recoverable %": round(mx, 2), "Status": st_})
    st.dataframe(pd.DataFrame(check_rows), hide_index=True, use_container_width=True)
    st.caption("Expected: 80/100/20 → 80.00% current, 83.33% max, SAFE · 60/100/40 → 71.43% max, IRREVERSIBLE · "
               "70/100/50 → 80.00% max, RECOVERING (below 75% now, recoverable).")

st.markdown(f'<div class="disclaimer">{DISCLAIMER}<br>'
            f'Semester window: {SEMESTER_START.isoformat()} → {SEMESTER_END.isoformat()}. '
            f'Today: {TODAY.isoformat()} (read from the system clock, not hardcoded). '
            f'Counting unit: 1 timetable period = 1 attendance hour.</div>', unsafe_allow_html=True)
