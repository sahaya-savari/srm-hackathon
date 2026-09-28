"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { getSections, getSection } from "@/lib/data";
import { useToday } from "@/lib/useToday";
import { countBySubject, SEMESTER_START, SEMESTER_END, type Weekday, type Slot } from "@/lib/calendar";
import { SectionPicker } from "@/components/planner/SectionPicker";
import { Calendar, ArrowRight } from "lucide-react";

export function TimetableView() {
  const sections = getSections();
  const searchParams = useSearchParams();
  const router = useRouter();
  const today = useToday() || "2026-09-28";

  const querySection = searchParams.get("section");
  const initialSectionId =
    querySection && sections.some((s) => s.id === querySection)
      ? querySection
      : "III-ECE-B";

  const [selectedId, setSelectedId] = useState<string>(initialSectionId);
  const currentSection = getSection(selectedId) || sections[0];

  const handleSelectSection = (newId: string) => {
    setSelectedId(newId);
    router.replace(`/timetable?section=${newId}`, { scroll: false });
  };

  const days: Weekday[] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const periods = [1, 2, 3, 4, 5, 6, 7, 8];

  // Subject statistics for the semester
  const totalScheduled = useMemo(() => {
    return countBySubject(currentSection, SEMESTER_START, SEMESTER_END);
  }, [currentSection]);

  const heldSoFar = useMemo(() => {
    return countBySubject(currentSection, SEMESTER_START, today);
  }, [currentSection, today]);

  const remaining = useMemo(() => {
    return countBySubject(currentSection, today, SEMESTER_END);
  }, [currentSection, today]);

  return (
    <div className="max-w-[1120px] mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[rgba(241,233,210,0.12)] pb-6">
        <div>
          <div className="inline-block bg-[#141A35] border border-[#FF9130]/40 text-[#FFB35C] px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider rounded-sm mb-2">
            Verified Timetable Grid
          </div>
          <h1 className="font-['Press_Start_2P'] text-lg sm:text-2xl text-[#F1E9D2] leading-tight">
            SECTION TIMETABLES
          </h1>
          <p className="text-xs text-[#CFC6A9] mt-1">
            Exact period-by-period weekly schedules transcribed cell-by-cell from official institutional scans.
          </p>
        </div>

        <Link
          href={`/planner?section=${currentSection.id}`}
          className="btn-block text-xs sm:text-sm font-bold uppercase tracking-wider inline-flex items-center gap-2 self-start sm:self-auto shrink-0"
        >
          <span>Plan with this section</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Section Selector */}
      <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 sm:p-5 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)]">
        <div className="flex items-center gap-2 mb-3">
          <Calendar className="w-4 h-4 text-[#FF9130]" />
          <h2 className="font-bold text-sm text-[#F1E9D2]">Choose Class Section</h2>
          <span className="text-xs text-[#CFC6A9]">({sections.length} sections verified)</span>
        </div>
        <SectionPicker selectedId={currentSection.id} onSelect={handleSelectSection} />
      </div>

      {/* Active Section Info Card */}
      <div className="bg-[#1C2448]/60 border border-[rgba(241,233,210,0.15)] p-4 rounded-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-lg font-bold font-mono text-[#F1E9D2] mr-3">
            {currentSection.id}
          </span>
          <span className="text-xs text-[#CFC6A9]">
            {currentSection.department} · Year {currentSection.year} · Sem {currentSection.semester}
            {currentSection.venue ? ` · Venue: ${currentSection.venue}` : ""}
          </span>
          {currentSection.note && (
            <span className="ml-2 text-[10px] bg-[#FF9130]/20 text-[#FFB35C] px-2 py-0.5 rounded border border-[#FF9130]/30">
              {currentSection.note}
            </span>
          )}
        </div>
        <div className="text-xs font-mono text-[#FFB35C]">
          {currentSection.totalWeeklyPeriods} classes/week · {currentSection.subjects.length} subjects
        </div>
      </div>

      {/* Timetable Weekly Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-['Press_Start_2P'] text-xs text-[#F1E9D2] uppercase tracking-wider">
            Weekly Schedule (Mon–Fri)
          </h2>
          <div className="flex items-center gap-4 text-[11px] text-[#CFC6A9]">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#6FA043]" /> High confidence
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#FF9130]" /> Verified handwriting
            </span>
          </div>
        </div>

        <div className="overflow-x-auto border border-[rgba(241,233,210,0.14)] rounded-sm bg-[#141A35] shadow-[4px_4px_0_0_rgba(0,0,0,0.4)]">
          <table className="w-full text-xs text-left border-collapse min-w-[760px]">
            <thead>
              <tr className="bg-[#0B0E1F] border-b border-[rgba(241,233,210,0.14)] text-[#CFC6A9]">
                <th className="p-3 w-28 uppercase tracking-wider font-bold">Day</th>
                {periods.map((p) => (
                  <th key={p} className="p-3 text-center border-l border-[rgba(241,233,210,0.1)]">
                    <span className="block font-bold text-[#F1E9D2]">P{p}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {days.map((day) => {
                const slots: Slot[] = currentSection.weekly[day] || [];
                const slotMap: Record<number, Slot> = {};
                slots.forEach((s) => {
                  slotMap[s.period] = s;
                });

                return (
                  <tr key={day} className="border-b border-[rgba(241,233,210,0.08)] hover:bg-[#1C2448]/30 transition-colors">
                    <td className="p-3 font-bold text-[#F1E9D2] bg-[#0B0E1F]/50">
                      {day}
                    </td>
                    {periods.map((p) => {
                      const slot = slotMap[p];
                      if (!slot) {
                        return (
                          <td key={p} className="p-2 border-l border-[rgba(241,233,210,0.08)] text-center text-[#CFC6A9]/30 font-mono">
                            —
                          </td>
                        );
                      }

                      const isHighConf = slot.confidence === "high";

                      return (
                        <td
                          key={p}
                          className={`p-2 border-l border-[rgba(241,233,210,0.08)] ${
                            slot.isLab ? "bg-[#7C4DFF]/15" : "bg-[#141A35]"
                          }`}
                        >
                          <div className="space-y-1">
                            <div className="flex items-center justify-between gap-1">
                              <span className="font-mono font-bold text-[#F1E9D2] text-[11px] truncate" title={slot.name}>
                                {slot.code}
                              </span>
                              <span
                                className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                                  isHighConf ? "bg-[#6FA043]" : "bg-[#FF9130]"
                                }`}
                                title={isHighConf ? "High confidence" : "Verified from faded/handwritten cell"}
                              />
                            </div>
                            <span className="text-[10px] text-[#CFC6A9] line-clamp-1" title={slot.name}>
                              {slot.name}
                            </span>
                            <div className="flex items-center justify-between text-[9px] text-[#CFC6A9]/70 pt-0.5">
                              <span>{slot.start}–{slot.end}</span>
                              {slot.isLab && <span className="text-[#A88BFF] font-semibold">LAB</span>}
                            </div>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Subject Counts Breakdown Table */}
      <div className="space-y-3">
        <h2 className="font-['Press_Start_2P'] text-xs text-[#F1E9D2] uppercase tracking-wider">
          Semester Occurrence Audit ({currentSection.subjects.length} subjects)
        </h2>
        <div className="overflow-x-auto border border-[rgba(241,233,210,0.14)] rounded-sm bg-[#141A35] shadow-[4px_4px_0_0_rgba(0,0,0,0.4)]">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="bg-[#0B0E1F] border-b border-[rgba(241,233,210,0.14)] text-[#CFC6A9]">
                <th className="p-3">Code</th>
                <th className="p-3">Subject Name</th>
                <th className="p-3">Faculty</th>
                <th className="p-3 text-center">Weekly Periods</th>
                <th className="p-3 text-center">Total Scheduled</th>
                <th className="p-3 text-center">Held So Far</th>
                <th className="p-3 text-center">Remaining</th>
              </tr>
            </thead>
            <tbody>
              {currentSection.subjects.map((sub) => {
                const total = totalScheduled[sub.code] || 0;
                const held = heldSoFar[sub.code] || 0;
                const rem = remaining[sub.code] || 0;

                return (
                  <tr key={sub.code} className="border-b border-[rgba(241,233,210,0.06)] hover:bg-[#1C2448]/20 transition-colors">
                    <td className="p-3 font-mono font-bold text-[#F1E9D2]">{sub.code}</td>
                    <td className="p-3 font-medium text-[#F1E9D2]">{sub.name}</td>
                    <td className="p-3 text-[#CFC6A9]">{sub.faculty || "—"}</td>
                    <td className="p-3 text-center font-mono text-[#FFB35C] font-semibold">{sub.weeklyPeriods}</td>
                    <td className="p-3 text-center font-mono text-[#F1E9D2] font-semibold">{total}</td>
                    <td className="p-3 text-center font-mono text-[#CFC6A9]">{held}</td>
                    <td className="p-3 text-center font-mono text-[#6FA043] font-bold">{rem}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
