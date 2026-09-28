"""
future_ml.py — Phase 2 architecture placeholder. NOT TRAINED, NOT WIRED IN.

Phase 1 (this app) is entirely deterministic: timetable -> calendar -> remaining
classes -> attendance mathematics -> risk -> planning. There is no student-level
attendance HISTORY in the current dataset (no per-class attended/absent events),
so no model can be trained or evaluated honestly yet. Nothing in this file is
imported by app.py or engine/*.py.

------------------------------------------------------------------------------
WHEN THIS BECOMES APPROPRIATE
------------------------------------------------------------------------------
Once the institution starts recording actual per-class attendance events (see
the event table below), a supervised layer can sit ALONGSIDE the deterministic
engine — never replacing it, since the deterministic maths (Section 3 of the
event field guide) is exact and needs no model.

------------------------------------------------------------------------------
FUTURE EVENT TABLE (one row per student x scheduled class)
------------------------------------------------------------------------------
student_id, section_id, subject_code, date, period, scheduled (bool),
conducted (bool), attended (bool), attendance_status (present/absent/OD/medical),
class_type, day_of_week, week_of_semester, recorded_at

------------------------------------------------------------------------------
CANDIDATE FEATURES (all computable from events strictly BEFORE prediction date
-- never leak future information, e.g. never use semester-final attendance to
predict a mid-semester outcome)
------------------------------------------------------------------------------
- recent_attendance_trend / rolling_attendance (7-day, 14-day windows)
- absence_streak / consecutive_absences
- attendance_volatility (variance of a rolling window)
- subject_level_absence_rate
- classes_remaining, attendance_headroom, recovery_burden (already computed
  deterministically by engine/attendance_engine.py -- reused as features)
- time_to_semester_end, week_of_semester
- day-of-week / period-of-day absence concentration

------------------------------------------------------------------------------
CANDIDATE TARGETS
------------------------------------------------------------------------------
- Model A: P(attend next scheduled class)                 [most data, earliest]
- Model B: P(final attendance < 75%)                       [needs full-semester outcomes]
- Model C: P(recover to 75% | currently below)              [conditioned subgroup]
- Model D: P(final attendance >= 90%)
- Model E: expected semester-end attendance %               [regression]

------------------------------------------------------------------------------
CANDIDATE MODEL
------------------------------------------------------------------------------
XGBoost (gradient-boosted trees) on the tabular feature set above is a
reasonable Phase-2 baseline: handles mixed numeric/categorical features well,
gives feature importances / SHAP explanations (matches the "every warning must
be explainable" principle), and needs no huge dataset to start with.

------------------------------------------------------------------------------
EVALUATION (do this properly or not at all)
------------------------------------------------------------------------------
- Precision, recall, F1, ROC-AUC, PR-AUC (PR-AUC matters more when at-risk
  students are a minority class), confusion matrix, calibration curve, Brier
  score. Recall on true at-risk students usually matters more than accuracy.
- TIME-AWARE split only: train on earlier weeks/semesters, validate on later
  weeks, test on a fully held-out future semester. Never a random row split
  (a single student's classes would leak information between train and test).
- No claim of predictive accuracy is made anywhere in this codebase because no
  labelled data exists yet. Do not train this module for the Phase-1 demo.
------------------------------------------------------------------------------
"""

# Intentionally no importable functions/classes yet — this file is
# documentation-as-code for the Phase 2 roadmap, not a working module.
