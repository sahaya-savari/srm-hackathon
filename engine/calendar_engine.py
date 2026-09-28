"""
Deterministic semester calendar engine.

Models SCHEDULED occurrences only. It cannot know which classes were actually
conducted: supply `holidays` / `cancellations` / `extra_days` when the
institution publishes them.

Counting unit: one timetable PERIOD (50 min) = one attendance hour. A 2-period
lab therefore counts as 2. Switch `unit="session"` to count a contiguous
block once instead (institution-dependent — UNKNOWN for this dataset).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from functools import lru_cache
import pandas as pd

SEMESTER_START = date(2026, 8, 29)
SEMESTER_END = date(2026, 11, 29)
DATA = Path(__file__).resolve().parents[1] / "data_clean" / "schedule.csv"
WEEKDAY_NAME = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

DISCLAIMER = ("The system currently models scheduled timetable occurrences. Actual attendance "
              "calculations may differ if institutional holidays, cancellations, exams, events, "
              "or timetable changes occurred.")


@dataclass
class CalendarConfig:
    start: date = SEMESTER_START
    end: date = SEMESTER_END
    holidays: set[date] = field(default_factory=set)            # whole-day closures
    cancellations: set[tuple[date, int]] = field(default_factory=set)  # (date, period)
    extra_days: dict[date, str] = field(default_factory=dict)   # e.g. a Saturday following "Monday" order
    unit: str = "period"                                         # "period" | "session"
    include_ambiguous: bool = True                               # keep C|D batch-lab rows as their own unit


@lru_cache(maxsize=1)
def _schedule() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    return df[df.valid_for_2026_27].copy()


def sections() -> list[str]:
    return sorted(_schedule().section_id.unique())


def weekly_template(section_id: str, cfg: CalendarConfig | None = None) -> pd.DataFrame:
    cfg = cfg or CalendarConfig()
    df = _schedule()
    df = df[df.section_id == section_id]
    if df.empty:
        raise ValueError(f"unknown or inactive section '{section_id}'")
    if not cfg.include_ambiguous:
        df = df[~df.slot.str.contains(r"\|")]
    if cfg.unit == "session":
        df = df[df.period == df.block_start]
    return df


def day_template_name(d: date, cfg: CalendarConfig) -> str | None:
    if d in cfg.holidays or d < cfg.start or d > cfg.end:
        return None
    if d in cfg.extra_days:
        return cfg.extra_days[d]
    return WEEKDAY_NAME[d.weekday()] if d.weekday() < 5 else None


def occurrences(section_id: str, frm: date, to: date, cfg: CalendarConfig | None = None) -> pd.DataFrame:
    """All scheduled class occurrences with frm <= date <= to (inclusive)."""
    cfg = cfg or CalendarConfig()
    tpl = weekly_template(section_id, cfg)
    rows = []
    d = max(frm, cfg.start)
    last = min(to, cfg.end)
    while d <= last:
        name = day_template_name(d, cfg)
        if name:
            day = tpl[tpl.day_of_week == name]
            for r in day.itertuples():
                if (d, r.period) in cfg.cancellations:
                    continue
                rows.append(dict(date=d, weekday=name, period=r.period, start=r.start_time, end=r.end_time,
                                 subject_code=r.subject_code, subject_name=r.subject_name,
                                 class_type=r.class_type, mapping_confidence=r.mapping_confidence))
        d += timedelta(days=1)
    return pd.DataFrame(rows, columns=["date", "weekday", "period", "start", "end", "subject_code",
                                       "subject_name", "class_type", "mapping_confidence"])


def count_by_subject(section_id: str, frm: date, to: date, cfg: CalendarConfig | None = None) -> dict[str, int]:
    occ = occurrences(section_id, frm, to, cfg)
    base = {c: 0 for c in weekly_template(section_id, cfg).subject_code.unique()}
    base.update(occ.groupby("subject_code").size().to_dict())
    return base


def semester_calendar(cfg: CalendarConfig | None = None) -> pd.DataFrame:
    """One row per date: weekday, status, scheduled class count per active section."""
    cfg = cfg or CalendarConfig()
    rows = []
    d = cfg.start
    secs = sections()
    while d <= cfg.end:
        name = day_template_name(d, cfg)
        row = dict(date=d, weekday=WEEKDAY_NAME[d.weekday()],
                   is_weekday=d.weekday() < 5, is_holiday=d in cfg.holidays,
                   is_scheduled_instruction_day=name is not None,
                   semester_status="instruction" if name else ("holiday" if d in cfg.holidays else "no-class"))
        for s in secs:
            row[s] = int((weekly_template(s, cfg).day_of_week == name).sum()) if name else 0
        rows.append(row)
        d += timedelta(days=1)
    return pd.DataFrame(rows)
