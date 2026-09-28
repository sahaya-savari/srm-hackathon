"""
RAW -> CLEANED -> NORMALIZED.

Maps every verbatim timetable cell to a subject slot, records *how* the
mapping was made (rule + confidence), and writes the canonical tables:

  data_clean/sections.csv   one row per section timetable
  data_clean/subjects.csv   one row per (section, slot)
  data_clean/schedule.csv   one row per (section, weekday, period)  <- weekly template
  data_clean/transforms.csv audit log of every non-trivial mapping
"""
import re, sys, csv
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data_raw"))
import transcription as T  # noqa: E402

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
DAY_FULL = dict(zip(DAYS, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]))

# Keyword rules for non-letter cells. (regex, slot-or-code resolver, class_type, confidence, rule note)
KEYWORD_RULES = [
    (r"^DLMS/EEC", "AMBIG:C|D", "lab", "low",
     "Batch lab shared by C (21BMC203J EEC) and D (21BMC204J DLMS); which course a given student attends on which day is not stated"),
    (r"^MPMC LAB", "B", "lab", "medium", "'MPMC' = Microcontrollers practical; only 3-0-2 course with MPMC content is slot B (21BMC302J)"),
    (r"^BIO DSP LAB", "C", "lab", "medium", "'BIO DSP' = Biomedical Signal Processing practical -> slot C (21BMC301J)"),
    (r"^PCB Lab/EC Lab", "AMBIG:F|G", "lab", "low", "Split cohort: ECE students -> PCB lab (F), EEE students -> EC lab (G)"),
    (r"^Che lab", "CODE:21CYB101J", "lab", "high", "Chemistry practical of 21CYB101J (3-1-2-5)"),
    (r"^PPS", "CODE:21CSS101J", "lab", "high", "Programming for Problem Solving practical of 21CSS101J"),
    (r"^PCB Lab", "CODE:21BTB102J", "lab", "medium", "PCB lab; course lists P=0 so this practical is not in the credit structure"),
    (r"^Workshop", "Workshop", "lab", "high", "Workshop = 21MES101L"),
    (r"^CDC", "CDC", "skill", "high", "CDC = Career Development Centre course"),
    (r"^NSS", "NSS", "activity", "high", ""),
    (r"^YOGA", "YOGA", "activity", "high", ""),
    (r"^German", "German", "theory", "high", ""),
    (r"^Japanese", "Japanese", "theory", "high", ""),
    (r"^LAB", "LAB", "lab", "high", "Lab row of subject table"),
    (r"^B-Proj", "B", "project", "medium", "'B-Proj' read as project hour of slot B (21ECC301P, a 'P' project-based course; makes B total 4 = L+T)"),
    (r"^[A-I]\s*/\s*[A-I]|^[A-I] IST\d+\s*/\s*[A-I]", "SPLIT", "theory", "low", "Split-cohort cell (two slots in one period)"),
]

def room_of(text):
    m = re.search(r"(IST\s*\d+[\d,]*|TB\s*-?\s*\d+|\b\d{3}(?:[/,]\d{3})?\b)", text)
    return m.group(0).replace(" ", "") if m else ""

def resolve(section_id, sec, raw):
    """Return list of (slot_key, class_type, confidence, rule)."""
    t = raw.strip()
    subj = sec["subjects"]
    for pat, target, ctype, conf, note in KEYWORD_RULES:
        if re.search(pat, t, flags=re.I):
            if target == "SPLIT":
                slots = re.findall(r"\b([A-I])\b(?=\s*IST|\s*/|$)", t)
                return [("|".join(dict.fromkeys(slots)), "theory", "low", note + f" -> {slots}")]
            if target.startswith("AMBIG:"):
                return [(target[6:], ctype, conf, note)]
            if target.startswith("CODE:"):
                code = target[5:]
                keys = [k for k, v in subj.items() if v[0] == code]
                return [(keys[0] if keys else code, ctype, conf, note)]
            if ctype == "theory" and target in subj:
                return [(target, ctype, conf, note)]
            return [(target, ctype, conf, note)]
    # plain slot letter, possibly followed by room: "A", "G-625", "G - 401", "H-TB-106", "I-108", "E IST602"
    m = re.match(r"^([A-I])(?:\s*[-–]\s*|\s+|$)", t)
    if m and m.group(1) in subj:
        slot = m.group(1)
        code, name, ltpc = subj[slot][:3]
        ctype = "skill" if code.startswith("21PDM") else ("practical" if code.endswith("L") else "theory")
        conf = "high" if t == slot or re.match(r"^[A-I] IST\d+$", t) else "high"
        note = "" if t == slot else "slot letter with room suffix"
        return [(slot, ctype, conf, note)]
    return [("UNMAPPED", "unknown", "none", f"no rule for '{t}'")]

def main():
    out = ROOT / "data_clean"; out.mkdir(exist_ok=True)
    sec_rows, sub_rows, sch_rows, log = [], [], [], []
    for sid, sec in T.SECTIONS.items():
        grid = getattr(T, sec["grid"])
        is_current = sec["academic_year"] == "2026-27"
        sec_rows.append(dict(
            section_id=sid, source_file=sec["source_file"], page=sec["page"],
            academic_year=sec["academic_year"], semester_type=sec["semester_type"],
            year=sec["year"], semester=sec["semester"], department=sec["dept"],
            home_venue=sec["venue"], bell_schedule=sec["grid"], approval_date=sec["approval_date"],
            valid_for_2026_27=is_current,
            status="ACTIVE" if is_current else "EXCLUDED_STALE (2024-25 timetable)"))
        for slot, (code, name, ltpc, fac, desig) in sec["subjects"].items():
            L = Tt = P = C = None
            if re.match(r"^\d-\d-\d-\d$", ltpc):
                L, Tt, P, C = map(int, ltpc.split("-"))
            sub_rows.append(dict(section_id=sid, slot=slot, subject_code=code, subject_name=name,
                                 ltpc=ltpc or "MISSING", L=L, T=Tt, P=P, credits=C,
                                 faculty=fac, designation=desig))
        occupied = {}
        for day, p1, p2, raw, note in sec["cells"]:
            maps = resolve(sid, sec, raw)
            for p in range(p1, p2 + 1):
                key = (day, p)
                if key in occupied:
                    log.append(dict(section_id=sid, day=day, period=p, raw=raw, issue="DUPLICATE_SLOT",
                                    detail=f"already {occupied[key]}"))
                occupied[key] = raw
                for slot, ctype, conf, rule in maps:
                    parts = slot.split("|")
                    code = "|".join(sec["subjects"][s][0] if s in sec["subjects"] else s for s in parts)
                    name = " | ".join(sec["subjects"][s][1] if s in sec["subjects"] else s for s in parts)
                    sch_rows.append(dict(
                        section_id=sid, day_of_week=DAY_FULL[day], weekday_idx=DAYS.index(day),
                        period=p, start_time=grid[p][0], end_time=grid[p][1],
                        block_start=p1, block_end=p2, block_len=p2 - p1 + 1,
                        raw_cell=raw, slot=slot, subject_code=code, subject_name=name,
                        class_type=ctype, is_lab=ctype in ("lab",), room=room_of(raw),
                        source_file=sec["source_file"], page=sec["page"],
                        visual_verified=True, handwritten=(note == "handwritten"), faded=(note == "faded"),
                        mapping_confidence=conf, mapping_rule=rule,
                        in_lunch_period=(p == 5), valid_for_2026_27=is_current))
                if rule and p == p1:
                    log.append(dict(section_id=sid, day=day, period=f"{p1}-{p2}" if p2 > p1 else p1,
                                    raw=raw, issue=f"MAPPING[{conf}]", detail=rule))
    pd.DataFrame(sec_rows).to_csv(out / "sections.csv", index=False)
    pd.DataFrame(sub_rows).to_csv(out / "subjects.csv", index=False)
    sch = pd.DataFrame(sch_rows)
    sch.to_csv(out / "schedule.csv", index=False)
    pd.DataFrame(log).to_csv(out / "transforms.csv", index=False)
    print(sch.groupby("section_id").size())
    print("unmapped:", (sch.slot == "UNMAPPED").sum())
    print(sch.mapping_confidence.value_counts())

if __name__ == "__main__":
    main()
