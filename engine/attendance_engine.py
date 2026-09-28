"""
Attendance mathematics + risk engine (pure functions, no UI, exact arithmetic).

Notation (per subject):
  A = classes attended so far, H = classes held so far, n = classes remaining,
  T = target fraction (Fraction(3,4) or Fraction(9,10)).

  required x   : smallest integer x in [0, n] with (A + x) / (H + n) >= T
                 x* = max(0, ceil(T*(H+n) - A));   feasible  <=>  x* <= n
  safe absences: n - x*                (only if feasible)
  max possible : (A + n) / (H + n)     (attend everything)
  min possible : A / (H + n)           (attend nothing)
  immediate skip budget: largest k with A / (H + k) >= T  ->  floor(A/T - H)
  required attendance rate (RAR): x* / n   (share of remaining classes that must be attended)

All targets are rules supplied by the institution/challenge, not evidence-based optima.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from fractions import Fraction
from math import ceil, floor
from datetime import date, timedelta
from typing import Optional

from calendar_engine import (CalendarConfig, count_by_subject, occurrences, weekly_template,
                             DISCLAIMER, SEMESTER_START, SEMESTER_END)

T75 = Fraction(3, 4)
T90 = Fraction(9, 10)


# --------------------------------------------------------------------------- core maths
def required_classes(A: int, H: int, n: int, T: Fraction) -> int:
    """Minimum future classes to attend (may exceed n => infeasible)."""
    _validate(A, H, n)
    return max(0, ceil(T * (H + n) - A))


def max_possible(A: int, H: int, n: int) -> Optional[Fraction]:
    return Fraction(A + n, H + n) if H + n else None


def min_possible(A: int, H: int, n: int) -> Optional[Fraction]:
    return Fraction(A, H + n) if H + n else None


def immediate_skip_budget(A: int, H: int, T: Fraction) -> int:
    """Consecutive classes that could be missed *right now* while staying >= T at that moment."""
    return max(0, floor(Fraction(A) / T - H)) if A else 0


def _validate(A, H, n):
    if min(A, H, n) < 0:
        raise ValueError("counts must be non-negative")
    if A > H:
        raise ValueError("classes attended cannot exceed classes held")


# --------------------------------------------------------------------------- statuses
def detention_status(A, H, n, T=T75) -> str:
    """LOCKED_SAFE | SAFE | CRITICAL | RECOVERING | IRREVERSIBLE — all defined mathematically."""
    if H + n == 0:
        return "NO_DATA"
    mx, mn = max_possible(A, H, n), min_possible(A, H, n)
    if mx < T:
        return "IRREVERSIBLE"
    if mn >= T:
        return "LOCKED_SAFE"          # safe even if every remaining class is missed
    x = required_classes(A, H, n, T)
    slack = n - x
    cur = Fraction(A, H) if H else None
    if cur is not None and cur >= T:
        return "SAFE" if slack > 0 else "CRITICAL"
    return "RECOVERING" if slack > 0 else "CRITICAL"


CHALLENGE_LABEL_75 = {"LOCKED_SAFE": "SAFE", "SAFE": "SAFE", "CRITICAL": "AT RISK",
                      "RECOVERING": "AT RISK", "IRREVERSIBLE": "IRREVERSIBLE DETENTION", "NO_DATA": "NO DATA"}


def goal90_status(A, H, n) -> str:
    """ACHIEVED | LOCKED | RECOVERABLE | IMPOSSIBLE (target 90%)."""
    if H + n == 0:
        return "NO_DATA"
    if max_possible(A, H, n) < T90:
        return "IMPOSSIBLE"
    if min_possible(A, H, n) >= T90:
        return "LOCKED"
    if H and Fraction(A, H) >= T90:
        return "ACHIEVED"            # currently >= 90%, must keep attending per required_to_90
    return "RECOVERABLE"


def headroom_band(safe_absences: Optional[int], weekly_freq: int) -> str:
    """PRODUCT HEURISTIC (not statistically validated). Bands are in *weeks of this subject*
    rather than raw classes, because weekly frequency in this dataset ranges 1..5, so '3 absences'
    means 3 weeks for a 1/wk course but under one week for a 5/wk course."""
    if safe_absences is None:
        return "NONE (infeasible)"
    if safe_absences == 0:
        return "CRITICAL"
    weeks = safe_absences / max(weekly_freq, 1)
    if weeks < 1:
        return "VERY_TIGHT"
    if weeks < 2:
        return "TIGHT"
    return "COMFORTABLE"


def explain(subject, A, H, n, T, status) -> str:
    pct = lambda f: f"{float(f) * 100:.1f}%"
    t = pct(T)
    if status in ("IRREVERSIBLE", "IMPOSSIBLE"):
        return (f"{subject}: even if you attend all {n} remaining classes, attendance can only reach "
                f"{pct(max_possible(A, H, n))}, which is below the {t} {'minimum' if T == T75 else 'goal'}.")
    x = required_classes(A, H, n, T)
    if status in ("LOCKED_SAFE", "LOCKED"):
        return f"{subject}: you stay at or above {t} even if you miss all {n} remaining classes."
    return (f"{subject}: attend at least {x} of the {n} remaining classes "
            f"(you can miss up to {n - x}) to finish at or above {t}.")


# --------------------------------------------------------------------------- inputs
@dataclass
class SubjectInput:
    subject_code: str
    attended: Optional[int] = None      # Mode A (exact)
    held: Optional[int] = None
    percent: Optional[float] = None     # Mode B (percentage only)
    percent_decimals: int = 0           # how the portal rounds (e.g. 0 -> "83%")


@dataclass
class PercentEstimate:
    held_estimate: int
    attended_candidates: list[int]
    attended_used: int
    consistent: bool
    warning: Optional[str]


def estimate_counts(percent: float, held_estimate: int, decimals: int = 0) -> PercentEstimate:
    """Percentage mode. Denominator = scheduled occurrences elapsed (ASSUMED all conducted).
    Picks the most conservative attended count consistent with the displayed (rounded) %."""
    if held_estimate <= 0:
        return PercentEstimate(0, [], 0, False, "No classes have been scheduled yet for this subject.")
    half = Fraction(5, 10 ** (decimals + 3))  # half a unit of the last displayed digit, as a fraction of 1
    p = Fraction(str(percent)) / 100
    lo, hi = p - half, p + half
    cands = [a for a in range(held_estimate + 1) if lo <= Fraction(a, held_estimate) < hi or
             (percent >= 100 and a == held_estimate)]
    if not cands:
        near = max(a for a in range(held_estimate + 1) if Fraction(a, held_estimate) <= p)  # conservative: round down
        return PercentEstimate(held_estimate, [], near, False,
                               f"{percent}% is not achievable with {held_estimate} scheduled classes "
                               f"(nearest is {near}/{held_estimate} = {near / held_estimate * 100:.1f}%). "
                               "Classes held probably differ from the timetable (holidays/cancellations/extra classes). "
                               "Enter exact 'attended' and 'held' counts for a reliable result.")
    w = None if len(cands) == 1 else (f"{percent}% matches {len(cands)} possible counts "
                                      f"({', '.join(f'{a}/{held_estimate}' for a in cands)}); using the lowest.")
    return PercentEstimate(held_estimate, cands, min(cands), True, w)


# --------------------------------------------------------------------------- main API
def plan(section_id: str, subjects: list[SubjectInput], today: Optional[date] = None,
         planning_date: Optional[date] = None, cfg: Optional[CalendarConfig] = None,
         gap_policy: str = "best") -> dict:
    """
    today          : dynamic by default (date.today()); classes before `today` are 'held so far'.
    planning_date  : first day the plan applies from (>= today, <= semester end).
    gap_policy     : classes between today and planning_date are not yet known ->
                     'best' (assume attended, default) or 'worst' (assume missed).
                     The other scenario is always reported under `otherGapScenario`.
    """
    cfg = cfg or CalendarConfig()
    today = today or date.today()
    planning_date = planning_date or today
    errors = []
    if planning_date < today:
        errors.append("planning_date must be on or after today")
    if planning_date > cfg.end:
        errors.append(f"planning_date must be on or before semester end {cfg.end}")
    if today < cfg.start:
        errors.append("semester has not started")
    if errors:
        return {"error": errors}

    tpl = weekly_template(section_id, cfg)
    weekly = tpl.groupby("subject_code").size().to_dict()
    names = tpl.groupby("subject_code").subject_name.first().to_dict()
    elapsed = count_by_subject(section_id, cfg.start, today - timedelta(days=1), cfg)
    gap = count_by_subject(section_id, today, planning_date - timedelta(days=1), cfg)
    remaining = count_by_subject(section_id, planning_date, cfg.end, cfg)

    out_subjects, warnings = [], []
    tot_A = tot_H = tot_n = 0
    for s in subjects:
        if s.subject_code not in weekly:
            warnings.append(f"{s.subject_code} is not in {section_id}'s timetable")
            continue
        mode, est = "exact", None
        if s.attended is not None and s.held is not None:
            A, H = s.attended, s.held
        elif s.percent is not None:
            mode = "estimated"
            est = estimate_counts(s.percent, elapsed[s.subject_code], s.percent_decimals)
            A, H = est.attended_used, est.held_estimate
            if est.warning:
                warnings.append(f"{s.subject_code}: {est.warning}")
        else:
            warnings.append(f"{s.subject_code}: no attendance input")
            continue
        _validate(A, H, 0)
        g = gap[s.subject_code]
        A_eff = A + (g if gap_policy == "best" else 0)
        H_eff = H + g
        n = remaining[s.subject_code]
        x75, x90 = required_classes(A_eff, H_eff, n, T75), required_classes(A_eff, H_eff, n, T90)
        st75, st90 = detention_status(A_eff, H_eff, n, T75), goal90_status(A_eff, H_eff, n)
        f75, f90 = x75 <= n, x90 <= n
        safe75 = n - x75 if f75 else None
        mx, mn = max_possible(A_eff, H_eff, n), min_possible(A_eff, H_eff, n)
        other = "worst" if gap_policy == "best" else "best"
        A_o = A + (g if other == "best" else 0)
        x75o, x90o = required_classes(A_o, H_eff, n, T75), required_classes(A_o, H_eff, n, T90)
        N_total = H_eff + n
        budget75 = N_total - ceil(T75 * N_total)            # = floor(25% of all classes)
        budget90 = N_total - ceil(T90 * N_total)
        rec = dict(
            subject=s.subject_code, subjectName=names[s.subject_code], mode=mode,
            currentAttendance=round(A / H * 100, 2) if H else None,
            classesHeld=H, classesAttended=A,
            classesBetweenTodayAndPlanningDate=g, gapPolicy=gap_policy,
            attendanceAtPlanningDate=round(A_eff / H_eff * 100, 2) if H_eff else None,  # statuses refer to this point
            classesHeldAtPlanningDate=H_eff, classesAttendedAtPlanningDate=A_eff,  # exact ints behind the % above
            classesRemaining=n, weeklyFrequency=weekly[s.subject_code],
            requiredTo75=x75 if f75 else None, requiredTo90=x90 if f90 else None,
            safeAbsences=safe75, safeAbsences90=(n - x90) if f90 else None,
            attendanceHeadroom=safe75, headroomBand=headroom_band(safe75, weekly[s.subject_code]),
            immediateSkipBudget75=immediate_skip_budget(A, H, T75),
            maximumPossibleAttendance=round(float(mx) * 100, 2) if mx is not None else None,
            minimumPossibleAttendance=round(float(mn) * 100, 2) if mn is not None else None,
            recoveryGap75_pp=round(max(0.0, 75 - A / H * 100), 2) if H else None,
            recoveryGap90_pp=round(max(0.0, 90 - A / H * 100), 2) if H else None,
            requiredAttendanceRate75=round(x75 / n, 3) if n else None,
            absenceBudget75=budget75, absenceBudget90=budget90, absencesUsed=H_eff - A_eff,
            otherGapScenario=dict(policy=other, requiredTo75=x75o if x75o <= n else None,
                                  requiredTo90=x90o if x90o <= n else None,
                                  detentionStatus=detention_status(A_o, H_eff, n, T75),
                                  recoveryStatus90=goal90_status(A_o, H_eff, n)) if g else None,
            detentionStatus=st75, recoveryStatus75=CHALLENGE_LABEL_75[st75], recoveryStatus90=st90,
            explanation75=explain(names[s.subject_code], A_eff, H_eff, n, T75, st75),
            explanation90=explain(names[s.subject_code], A_eff, H_eff, n, T90, st90),
        )
        if est:
            rec["estimate"] = asdict(est)
        out_subjects.append(rec)
        tot_A += A_eff; tot_H += H_eff; tot_n += n

    risky = [r for r in out_subjects if r["recoveryStatus75"] != "SAFE"]
    irrev = [r for r in out_subjects if r["detentionStatus"] == "IRREVERSIBLE"]
    feas = [r for r in out_subjects if r["safeAbsences"] is not None]
    overall = ("IRREVERSIBLE" if irrev else "AT RISK" if risky else "SAFE") if out_subjects else "NO DATA"
    wk_start = today - timedelta(days=today.weekday())
    this_week = occurrences(section_id, today, wk_start + timedelta(days=6), cfg)
    return dict(
        section=section_id, today=str(today), planningDate=str(planning_date),
        semesterStart=str(cfg.start), semesterEnd=str(cfg.end),
        classesRemaining=sum(remaining.values()),
        classesRemainingTrackedSubjects=tot_n,
        overallRisk=overall, subjectsAtRisk=len(risky), irreversibleSubjects=len(irrev),
        requiredAttendance={r["subject"]: {"to75": r["requiredTo75"], "to90": r["requiredTo90"]} for r in out_subjects},
        smartMetrics=dict(
            aggregateAttendance=round(tot_A / tot_H * 100, 2) if tot_H else None,
            mostAtRiskSubject=min(out_subjects, key=lambda r: r["maximumPossibleAttendance"] or 0)["subject"] if out_subjects else None,
            lowestBufferSubject=min(feas, key=lambda r: r["safeAbsences"])["subject"] if feas else None,
            fewestRemainingSubject=min(out_subjects, key=lambda r: r["classesRemaining"])["subject"] if out_subjects else None,
            highestRequiredRateSubject=max(out_subjects, key=lambda r: r["requiredAttendanceRate75"] or 0)["subject"] if out_subjects else None,
            classesToday=int((occurrences(section_id, today, today, cfg)).shape[0]),
            classesRemainingThisWeek=int(this_week.shape[0]),
        ),
        subjects=out_subjects, warnings=warnings, disclaimer=DISCLAIMER,
    )


def trajectory(A: int, H: int, n: int) -> list[dict]:
    """Best / worst / minimum-to-75 / minimum-to-90 paths, class by class (attend-first ordering)."""
    x75, x90 = required_classes(A, H, n, T75), required_classes(A, H, n, T90)
    pts = []
    for k in range(n + 1):
        d = H + k
        pts.append(dict(k=k,
                        best=(A + k) / d if d else None,
                        worst=A / d if d else None,
                        target75=(A + min(k, x75)) / d if d and x75 <= n else None,
                        target90=(A + min(k, x90)) / d if d and x90 <= n else None))
    return pts
