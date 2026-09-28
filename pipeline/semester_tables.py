"""Builds the theoretical semester occurrence table + dataset-derived metric analysis."""
import sys, json
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from calendar_engine import sections, occurrences, semester_calendar, count_by_subject, weekly_template, SEMESTER_START, SEMESTER_END
from attendance_engine import plan, SubjectInput, required_classes, T75, T90
TODAY = date(2026, 9, 28)
R = ROOT / "reports"

semester_calendar().to_csv(ROOT / "data_clean" / "semester_calendar.csv", index=False)
occ = pd.concat([occurrences(s, SEMESTER_START, SEMESTER_END).assign(section_id=s) for s in sections()])
occ.to_csv(ROOT / "data_clean" / "semester_occurrences_scheduled.csv", index=False)

rows = []
for s in sections():
    tpl = weekly_template(s)
    w = tpl.groupby("subject_code").size()
    el = count_by_subject(s, SEMESTER_START, TODAY - timedelta(days=1))
    rem = count_by_subject(s, TODAY, SEMESTER_END)
    for c in w.index:
        N = el[c] + rem[c]
        rows.append(dict(section_id=s, subject_code=c, subject_name=tpl[tpl.subject_code == c].subject_name.iloc[0],
                         weekly=int(w[c]), semester_total=N, held_by_today=el[c], remaining_from_today=rem[c],
                         max_total_absences_75=N - required_classes(0, 0, N, T75),
                         max_total_absences_90=N - required_classes(0, 0, N, T90)))
df = pd.DataFrame(rows); df.to_csv(R / "subject_semester_counts.csv", index=False)
print(df.groupby("weekly").agg(subjects=("subject_code", "size"), semester_total=("semester_total", "first"),
      abs75=("max_total_absences_75", "first"), abs90=("max_total_absences_90", "first")).to_string())
print("section totals remaining from today:"); print(df.groupby("section_id")[["semester_total","held_by_today","remaining_from_today"]].sum().to_string())

# point-of-no-return: for a student who has missed EVERY class so far, last week they can still recover to 75%
pnr = []
for w in sorted(df.weekly.unique()):
    N = 13 * w
    for wk in range(14):
        H = wk * w; n = N - H
        if required_classes(0, H, n, T75) > n:
            pnr.append(dict(weekly=w, first_irrecoverable_week_if_0pct=wk)); break
    # student at 60% after k weeks
    for wk in range(1, 14):
        H = wk * w; A = int(0.6 * H); n = N - H
        if required_classes(A, H, n, T75) > n:
            pnr[-1]["first_irrecoverable_week_if_60pct"] = wk; break
print(pd.DataFrame(pnr).to_string())

# worked example
ex = plan("III-ECE-B", [SubjectInput("21MAB302T", 11, 16), SubjectInput("21ECC301P", 12, 16),
                        SubjectInput("21ECC303T", percent=58), SubjectInput("21ECC311L", 16, 16),
                        SubjectInput("21LEM301T", 1, 4)],
          today=TODAY, planning_date=date(2026, 10, 15))
json.dump(ex, open(R / "example_output_III-ECE-B.json", "w"), indent=2, default=str)
for s in ex["subjects"]:
    print(s["subject"], s["mode"], s["classesAttended"], "/", s["classesHeld"], "gap", s["classesBetweenTodayAndPlanningDate"],
          "rem", s["classesRemaining"], "x75", s["requiredTo75"], "x90", s["requiredTo90"], "safe", s["safeAbsences"],
          "max", s["maximumPossibleAttendance"], s["detentionStatus"], s["recoveryStatus90"], s["headroomBand"])
    print("   ", s["explanation75"])
print(ex["overallRisk"], ex["smartMetrics"], ex["warnings"])
