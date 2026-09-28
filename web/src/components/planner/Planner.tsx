"use client";

import React, { useState, useMemo } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useToday } from "@/lib/useToday";
import { getSections, getSection } from "@/lib/data";
import { plan, type SubjectInput, type PlanResult, type PlanError, type SubjectPlan } from "@/lib/attendance";
import { countBySubject, SEMESTER_START, SEMESTER_END } from "@/lib/calendar";
import { safeGetStorage, safeSetStorage } from "@/lib/storage";

import { PlannerSkeleton } from "./PlannerSkeleton";
import { SectionPicker } from "./SectionPicker";
import { AttendanceTable, type AttendanceRowState } from "./AttendanceTable";
import { PlanningDate } from "./PlanningDate";
import { IrreversibleAlert } from "./IrreversibleAlert";
import { StatusBanner } from "./StatusBanner";
import { KpiGrid } from "./KpiGrid";
import { SubjectCard } from "./SubjectCard";



export function Planner() {
  const today = useToday();
  const searchParams = useSearchParams();
  const router = useRouter();

  const sections = getSections();
  const querySection = searchParams.get("section");
  const initialSectionId =
    (querySection && sections.some((s) => s.id === querySection))
      ? querySection
      : safeGetStorage<string>("ap_last_section", "III-ECE-B");

  const [sectionId, setSectionId] = useState<string>(initialSectionId);
  const currentSection = getSection(sectionId) || sections[0];

  const [customPlanningDate, setCustomPlanningDate] = useState<string | null>(null);
  const planningDate = customPlanningDate ?? (today || "2026-09-28");
  const [gapPolicy, setGapPolicy] = useState<"attend" | "miss">("attend");

  const handleSelectSection = (newId: string) => {
    setSectionId(newId);
    safeSetStorage("ap_last_section", newId);
    router.replace(`/planner?section=${newId}`, { scroll: false });
  };

  const heldSoFar = useMemo(() => {
    if (!today) return {};
    return countBySubject(currentSection, SEMESTER_START, today);
  }, [currentSection, today]);

  const gapClasses = useMemo(() => {
    if (!today || planningDate <= today) return 0;
    const gapCounts = countBySubject(currentSection, today, planningDate);
    return Object.values(gapCounts).reduce((a, b) => a + b, 0);
  }, [currentSection, today, planningDate]);

  // Attendance inputs state for current section
  const [rows, setRows] = useState<AttendanceRowState[]>(() => {
    const saved = safeGetStorage<Record<string, { mode: "percent" | "exact"; percentRaw: string; attendedRaw: string; heldRaw: string }>>(
      `ap_inputs_${currentSection.id}`,
      {}
    );

    return currentSection.subjects.map((sub) => {
      const s = saved[sub.code];
      const est = heldSoFar[sub.code] || 16;
      return {
        code: sub.code,
        name: sub.name,
        weeklyPeriods: sub.weeklyPeriods,
        mode: s?.mode || "percent",
        percentRaw: s?.percentRaw !== undefined ? s.percentRaw : "75",
        attendedRaw: s?.attendedRaw || "",
        heldRaw: s?.heldRaw || "",
        heldEstimate: est,
      };
    });
  });

  // Safe update when section switch happens
  const onSectionChange = (newSecId: string) => {
    handleSelectSection(newSecId);
    const targetSection = getSection(newSecId) || sections[0];
    const saved = safeGetStorage<Record<string, { mode: "percent" | "exact"; percentRaw: string; attendedRaw: string; heldRaw: string }>>(
      `ap_inputs_${targetSection.id}`,
      {}
    );
    const ests = today ? countBySubject(targetSection, SEMESTER_START, today) : {};
    setRows(
      targetSection.subjects.map((sub) => {
        const s = saved[sub.code];
        const est = ests[sub.code] || 16;
        return {
          code: sub.code,
          name: sub.name,
          weeklyPeriods: sub.weeklyPeriods,
          mode: s?.mode || "percent",
          percentRaw: s?.percentRaw !== undefined ? s.percentRaw : "75",
          attendedRaw: s?.attendedRaw || "",
          heldRaw: s?.heldRaw || "",
          heldEstimate: est,
        };
      })
    );
  };

  const persistRows = (newRows: AttendanceRowState[]) => {
    const toSave: Record<string, { mode: "percent" | "exact"; percentRaw: string; attendedRaw: string; heldRaw: string }> = {};
    for (const r of newRows) {
      toSave[r.code] = {
        mode: r.mode,
        percentRaw: r.percentRaw,
        attendedRaw: r.attendedRaw,
        heldRaw: r.heldRaw,
      };
    }
    safeSetStorage(`ap_inputs_${currentSection.id}`, toSave);
  };

  const handleChangeRow = (code: string, updates: Partial<AttendanceRowState>) => {
    setRows((prev) => {
      const updated = prev.map((r) => (r.code === code ? { ...r, ...updates } : r));
      persistRows(updated);
      return updated;
    });
  };

  const handleSetAllPercent = (pct: string) => {
    setRows((prev) => {
      const updated = prev.map((r) => ({
        ...r,
        mode: "percent" as const,
        percentRaw: pct,
      }));
      persistRows(updated);
      return updated;
    });
  };

  const handleClearAll = () => {
    setRows((prev) => {
      const updated = prev.map((r) => ({
        ...r,
        percentRaw: "",
        attendedRaw: "",
        heldRaw: "",
      }));
      persistRows(updated);
      return updated;
    });
  };

  const { validInputs, rowErrors } = useMemo(() => {
    const errors: Record<string, string> = {};
    const valid: SubjectInput[] = [];

    for (const r of rows) {
      if (r.mode === "percent") {
        if (r.percentRaw.trim() === "") {
          errors[r.code] = "Enter attendance % or switch to exact counts";
          continue;
        }
        const p = parseFloat(r.percentRaw);
        if (isNaN(p)) {
          errors[r.code] = "Must be a valid number";
          continue;
        }
        if (p < 0 || p > 100) {
          errors[r.code] = "Must be between 0% and 100%";
          continue;
        }
        valid.push({
          code: r.code,
          mode: "percent",
          percent: p,
          percentRaw: r.percentRaw.trim(),
        });
      } else {
        if (r.attendedRaw.trim() === "" || r.heldRaw.trim() === "") {
          errors[r.code] = "Enter both attended and held counts";
          continue;
        }
        const a = parseInt(r.attendedRaw, 10);
        const h = parseInt(r.heldRaw, 10);
        if (isNaN(a) || isNaN(h)) {
          errors[r.code] = "Counts must be whole numbers";
          continue;
        }
        if (a < 0 || h < 0) {
          errors[r.code] = "Counts cannot be negative";
          continue;
        }
        if (a > h) {
          errors[r.code] = "Attended cannot exceed held";
          continue;
        }
        valid.push({
          code: r.code,
          mode: "exact",
          attended: a,
          held: h,
        });
      }
    }

    return { validInputs: valid, rowErrors: errors };
  }, [rows]);

  const planResult = useMemo<PlanResult | PlanError | null>(() => {
    if (!today || validInputs.length === 0) return null;
    return plan(currentSection, validInputs, today, planningDate, gapPolicy);
  }, [currentSection, validInputs, today, planningDate, gapPolicy]);

  if (!today) {
    return <PlannerSkeleton />;
  }

  const statusRank: Record<string, number> = {
    IRREVERSIBLE: 0,
    CRITICAL: 1,
    RECOVERING: 2,
    SAFE: 3,
    LOCKED_SAFE: 4,
    NO_DATA: 5,
  };

  const sortedSubjects: SubjectPlan[] = planResult && planResult.ok
    ? [...planResult.subjects].sort((a, b) => {
        const rankA = statusRank[a.detention] ?? 99;
        const rankB = statusRank[b.detention] ?? 99;
        if (rankA !== rankB) return rankA - rankB;
        const safeA = a.safeAbsences75 ?? 999;
        const safeB = b.safeAbsences75 ?? 999;
        return safeA - safeB;
      })
    : [];

  const isSemesterEnded = today > SEMESTER_END;
  const isSemesterNotStarted = today < SEMESTER_START;

  return (
    <div className="max-w-[1120px] mx-auto px-4 py-8">
      {isSemesterEnded && (
        <div className="mb-6 p-4 bg-[#141A35] border-2 border-[#FF9130] rounded-sm text-[#FFB35C] text-sm flex items-center justify-between">
          <span>The 2026 semester has concluded (ended 29 Nov 2026). Displaying final recorded standing.</span>
        </div>
      )}
      {isSemesterNotStarted && (
        <div className="mb-6 p-4 bg-[#141A35] border-2 border-[#6FA043] rounded-sm text-[#6FA043] text-sm flex items-center justify-between">
          <span>The semester has not started yet (begins 29 Aug 2026). Showing projected baseline.</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: 3 Steps */}
        <div className="lg:col-span-5 space-y-6 lg:sticky lg:top-20">
          <div className="space-y-1">
            <h1 className="font-['Press_Start_2P'] text-lg sm:text-xl text-[#F1E9D2] leading-snug">
              ATTENDANCE PLANNER
            </h1>
            <p className="text-xs text-[#CFC6A9]">
              Configure your section and attendance to calculate remaining classes and recovery room.
            </p>
          </div>

          {/* STEP 1: Section */}
          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 sm:p-5 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)]">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-5 h-5 rounded-full bg-[#FF9130] text-[#1B140C] font-bold text-xs flex items-center justify-center">
                1
              </span>
              <h2 className="font-bold text-sm text-[#F1E9D2]">Your Class Section</h2>
            </div>
            <SectionPicker selectedId={sectionId} onSelect={onSectionChange} />
          </div>

          {/* STEP 2: Attendance Inputs */}
          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 sm:p-5 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)]">
            <div className="flex items-center justify-between gap-2 mb-3">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-[#FF9130] text-[#1B140C] font-bold text-xs flex items-center justify-center">
                  2
                </span>
                <h2 className="font-bold text-sm text-[#F1E9D2]">Your Current Attendance</h2>
              </div>
              <span className="text-[11px] text-[#A88BFF]">
                {validInputs.length}/{rows.length} valid
              </span>
            </div>
            <AttendanceTable
              rows={rows}
              onChangeRow={handleChangeRow}
              onSetAllPercent={handleSetAllPercent}
              onClearAll={handleClearAll}
              errors={rowErrors}
            />
          </div>

          {/* STEP 3: Planning Date */}
          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 sm:p-5 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)]">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-5 h-5 rounded-full bg-[#FF9130] text-[#1B140C] font-bold text-xs flex items-center justify-center">
                3
              </span>
              <h2 className="font-bold text-sm text-[#F1E9D2]">Plan From Date</h2>
            </div>
            <PlanningDate
              today={today}
              planningDate={planningDate}
              gapPolicy={gapPolicy}
              onDateChange={setCustomPlanningDate}
              onPolicyChange={setGapPolicy}
              gapClasses={gapClasses}
            />
          </div>
        </div>

        {/* Right Column: Instant Results */}
        <div className="lg:col-span-7 space-y-6">
          {planResult && planResult.ok ? (
            <div>
              <IrreversibleAlert subjects={planResult.subjects} />

              <StatusBanner
                overallStatus={planResult.overallStatus}
                overall={planResult.overall}
                planningDate={planningDate}
                today={today}
              />

              <KpiGrid
                classesLeftInSemester={planResult.classesLeftInSemester}
                overall={planResult.overall}
                atRiskCount={planResult.atRiskCount}
                irreversibleCount={planResult.irreversibleCount}
                totalSubjects={planResult.subjects.length}
                planningDate={planningDate}
              />

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-['Press_Start_2P'] text-xs text-[#F1E9D2] uppercase tracking-wider">
                    Subject Breakdown ({planResult.subjects.length})
                  </h3>
                  <span className="text-xs text-[#CFC6A9]">
                    Sorted by risk urgency
                  </span>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {sortedSubjects.map((sub) => {
                    const matchedSubject = currentSection.subjects.find((s) => s.code === sub.code);
                    return (
                      <SubjectCard
                        key={sub.code}
                        subject={sub}
                        weeklyPeriods={matchedSubject?.weeklyPeriods}
                        planningDate={planningDate}
                        today={today}
                      />
                    );
                  })}
                </div>
              </div>
            </div>
          ) : planResult && !planResult.ok ? (
            <div className="p-6 bg-[#141A35] border-2 border-[#E33D2E] rounded-sm text-[#F1E9D2] space-y-2">
              <h3 className="font-bold text-base text-[#E33D2E]">Calculation Error</h3>
              <ul className="list-disc list-inside text-xs space-y-1 text-[#CFC6A9]">
                {planResult.errors.map((e: string, idx: number) => (
                  <li key={idx}>{e}</li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="p-12 text-center bg-[#141A35] border border-[rgba(241,233,210,0.1)] rounded-sm space-y-3">
              <span className="text-3xl block">🎓</span>
              <h3 className="font-bold text-base text-[#F1E9D2]">Enter your attendance</h3>
              <p className="text-xs text-[#CFC6A9] max-w-sm mx-auto">
                Fill in attendance for at least one subject on the left to see your full attendance plan, recovery calculations, and detention alerts.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
