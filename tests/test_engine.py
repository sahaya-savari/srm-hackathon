"""Deterministic validation suite (prompt §29 tests 1-10 + §30 edge cases)."""
import sys
from datetime import date
from fractions import Fraction
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from attendance_engine import (required_classes, detention_status, goal90_status, estimate_counts,
                               max_possible, immediate_skip_budget, plan, SubjectInput, T75, T90, trajectory)
from calendar_engine import count_by_subject, CalendarConfig, occurrences, semester_calendar

TODAY = date(2026, 9, 28)


# ---------------------------------------------------------------- §29 tests
def test_1_full_attendance_no_recovery():
    assert required_classes(20, 20, 30, T75) == 18          # must still attend 18 of 30 to hold 75% at end
    assert detention_status(20, 20, 30) == "SAFE"
    assert detention_status(40, 40, 10) == "LOCKED_SAFE"     # 40/50 = 80% even if all missed

def test_2_exactly_75_is_at_threshold():
    assert detention_status(15, 20, 0) == "SAFE" or detention_status(15, 20, 0) == "LOCKED_SAFE"
    assert required_classes(15, 20, 10, T75) == 8            # ceil(.75*30 - 15) = ceil(7.5)
    assert required_classes(15, 20, 0, T75) == 0

def test_3_below_75_recoverable():
    assert required_classes(10, 20, 30, T75) == 28           # ceil(37.5 - 10) = 28 <= 30
    assert detention_status(10, 20, 30) == "RECOVERING"

def test_4_irreversible_detention():
    assert max_possible(5, 20, 10) == Fraction(15, 30)
    assert detention_status(5, 20, 10) == "IRREVERSIBLE"
    assert required_classes(5, 20, 10, T75) > 10

def test_5_between_75_and_90():
    assert detention_status(16, 20, 20) == "SAFE"
    assert goal90_status(16, 20, 20) == "RECOVERABLE"

def test_6_exactly_enough_for_90():
    # (A+n)/(H+n) == 0.9 exactly: 8/10 then attend 10 -> 18/20
    assert required_classes(8, 10, 10, T90) == 10
    assert goal90_status(8, 10, 10) == "RECOVERABLE"

def test_7_90_impossible():
    assert goal90_status(7, 10, 10) == "IMPOSSIBLE"          # max 17/20 = 85%

def test_8_planning_on_semester_end_zero_remaining():
    # 29 Nov 2026 is a Sunday -> nothing scheduled
    assert sum(count_by_subject("IV-ECE-A", date(2026, 11, 29), date(2026, 11, 29)).values()) == 0
    r = plan("IV-ECE-A", [SubjectInput("21ECE461T", 30, 36)], today=TODAY, planning_date=date(2026, 11, 29))
    assert r["classesRemaining"] == 0

def test_9_planning_after_semester_end_invalid():
    r = plan("IV-ECE-A", [SubjectInput("21ECE461T", 10, 12)], today=TODAY, planning_date=date(2026, 12, 1))
    assert "error" in r

def test_10_percentage_inconsistent_with_count():
    est = estimate_counts(83, 12, 0)                         # 12 held: 10/12=83.3% OK
    assert est.consistent and est.attended_used == 10
    bad = estimate_counts(95, 12, 0)                         # 11/12=91.7, 12/12=100 -> 95% impossible
    assert not bad.consistent and "not achievable" in bad.warning

# ---------------------------------------------------------------- §30 edge cases
def test_zero_remaining():
    assert required_classes(10, 20, 0, T75) == 5 and detention_status(10, 20, 0) == "IRREVERSIBLE"

def test_exactly_90():
    assert goal90_status(18, 20, 0) in ("LOCKED", "ACHIEVED")

def test_one_remaining_class():
    assert required_classes(14, 19, 1, T75) == 1              # 15/20 = 75% exactly
    assert detention_status(14, 19, 1) == "CRITICAL"

def test_float_boundary_uses_exact_arithmetic():
    # With floats, 0.55 * 100 = 55.00000000000001 -> ceil gives 56 (wrong). Fractions give 55.
    # (For 75%/90% floats happen to be safe up to 240 classes, but configurable targets are not.)
    import math
    assert math.ceil(0.55 * 100) == 56
    assert required_classes(0, 0, 100, Fraction(55, 100)) == 55
    assert required_classes(0, 0, 30, T90) == 27

def test_rounding_ambiguity_picks_conservative():
    est = estimate_counts(75, 40, 0)                          # 30/40=75.0 only (29.8..30.2)
    assert est.attended_used == 30
    est = estimate_counts(80, 200, 0)                         # 159..160 -> 79.5..80.0
    assert est.attended_used == min(est.attended_candidates)

def test_invalid_counts():
    with pytest.raises(ValueError):
        required_classes(11, 10, 5, T75)

def test_immediate_skip_budget():
    assert immediate_skip_budget(18, 20, T75) == 4            # 18/24 = 75%

def test_trajectory_endpoints():
    t = trajectory(10, 20, 30)
    assert t[-1]["best"] == pytest.approx(40 / 50) and t[-1]["worst"] == pytest.approx(10 / 50)
    assert t[-1]["target75"] >= 0.75

# ---------------------------------------------------------------- calendar
def test_semester_week_structure():
    cal = semester_calendar()
    assert cal.is_scheduled_instruction_day.sum() == 65       # 13 full Mon-Fri weeks
    assert str(cal.date.iloc[0]) == "2026-08-29" and cal.weekday.iloc[0] == "Saturday"

def test_holiday_removes_classes():
    cfg = CalendarConfig(holidays={date(2026, 10, 2)})       # a Friday
    a = count_by_subject("IV-ECE-A", date(2026, 10, 2), date(2026, 10, 2))
    b = count_by_subject("IV-ECE-A", date(2026, 10, 2), date(2026, 10, 2), cfg)
    assert sum(a.values()) == 4 and sum(b.values()) == 0

def test_lab_counts_per_period_or_session():
    per = count_by_subject("III-ECE-A", date(2026, 8, 31), date(2026, 9, 4))["21ECC311L"]
    ses = count_by_subject("III-ECE-A", date(2026, 8, 31), date(2026, 9, 4), CalendarConfig(unit="session"))["21ECC311L"]
    assert (per, ses) == (4, 2)

def test_plan_contract():
    r = plan("III-ECE-B", [SubjectInput("21MAB302T", percent=81)], today=TODAY, planning_date=date(2026, 10, 15))
    s = r["subjects"][0]
    for k in ["subject", "currentAttendance", "classesHeld", "classesAttended", "classesRemaining", "requiredTo75",
              "requiredTo90", "safeAbsences", "maximumPossibleAttendance", "recoveryStatus75", "recoveryStatus90",
              "attendanceHeadroom"]:
        assert k in s
    assert s["classesHeld"] == 16 and s["mode"] == "estimated"   # 4 per week x 4 weeks elapsed
    assert r["disclaimer"]

def test_safe_absences_equal_budget_minus_used():
    from math import ceil
    for A, H, n in [(11, 16, 36), (30, 36, 3), (20, 20, 19), (5, 9, 30)]:
        N = H + n
        x = required_classes(A, H, n, T75)
        if x <= n:
            assert n - x == (N - ceil(T75 * N)) - (H - A)

def test_gap_scenarios_reported():
    r = plan("III-ECE-B", [SubjectInput("21MAB302T", 11, 16)], today=TODAY, planning_date=date(2026, 10, 15))
    s = r["subjects"][0]
    assert s["gapPolicy"] == "best" and s["detentionStatus"] != "IRREVERSIBLE"
    assert s["otherGapScenario"]["policy"] == "worst" and s["otherGapScenario"]["detentionStatus"] == "IRREVERSIBLE"
