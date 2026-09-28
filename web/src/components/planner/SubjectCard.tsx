"use client";

import React, { useState } from "react";
import { StatusChip } from "@/components/ui/StatusChip";
import { Goal90Badge } from "@/components/ui/Goal90Badge";
import { ChevronDown, ChevronUp, AlertCircle } from "lucide-react";
import { UI_STATUS, type SubjectPlan, type Goal90Status, type UiStatus } from "@/lib/attendance";

interface SubjectCardProps {
  subject: SubjectPlan;
  weeklyPeriods?: number;
  planningDate: string;
  today: string;
}

export function SubjectCard({ subject, weeklyPeriods, planningDate, today }: SubjectCardProps) {
  const [showGoal90, setShowGoal90] = useState(false);
  const isFuture = planningDate > today;

  const currentPct = subject.currentPct !== null ? Math.min(100, Math.max(0, subject.currentPct)) : 0;
  const maxPossible = subject.maxPossible !== null ? Math.min(100, Math.max(0, subject.maxPossible)) : 0;
  const currentPctStr = subject.currentPct !== null ? `${subject.currentPct.toFixed(2)}%` : "—";
  const maxPossibleStr = subject.maxPossible !== null ? `${subject.maxPossible.toFixed(2)}%` : "—";

  // Determine progress bar color based on status
  const barColor =
    subject.uiStatus === "SAFE"
      ? "bg-[#6FA043]"
      : subject.uiStatus === "AT RISK"
      ? "bg-[#FF9130]"
      : "bg-[#E33D2E]";

  return (
    <div className="bg-[#141A35] border border-[rgba(241,233,210,0.14)] p-4 sm:p-5 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <h4 className="font-bold text-[#F1E9D2] text-sm sm:text-base leading-snug">
              {subject.name}
            </h4>
            <div className="flex items-center gap-2 mt-1 text-xs text-[#CFC6A9]">
              <span className="font-mono font-medium">{subject.code}</span>
              {weeklyPeriods && <span>· {weeklyPeriods} classes/wk</span>}
            </div>
          </div>
          <div className="flex flex-col items-end gap-1.5 shrink-0">
            <StatusChip status={subject.uiStatus as UiStatus} size="sm" />
            <Goal90Badge
              status={subject.goal90 as Goal90Status}
              maxPossible={subject.maxPossible}
              required={subject.required90}
              remaining={subject.remaining}
            />
          </div>
        </div>

        {/* Attendance Visual Bar */}
        <div className="my-4">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="font-mono text-[#F1E9D2]">
              Current: <strong>{currentPctStr}</strong>
              <span className="text-[#CFC6A9] ml-1.5">
                ({subject.attended}/{subject.held} held)
              </span>
            </span>
            <span className="text-[11px] text-[#CFC6A9]">
              Max: <strong className="font-mono text-[#F1E9D2]">{maxPossibleStr}</strong>
            </span>
          </div>

          <div className="relative w-full h-4 bg-[#0B0E1F] rounded-sm overflow-hidden border border-[rgba(241,233,210,0.12)]">
            {/* Ghost bar for max possible */}
            <div
              className="absolute top-0 bottom-0 left-0 bg-[#F1E9D2]/15 transition-all duration-300"
              style={{ width: `${maxPossible}%` }}
              title={`Max possible: ${maxPossibleStr}`}
            />

            {/* Current attendance bar */}
            <div
              className={`absolute top-0 bottom-0 left-0 ${barColor} transition-all duration-300`}
              style={{ width: `${currentPct}%` }}
              title={`Current: ${currentPctStr}`}
            />

            {/* 75% threshold marker */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-[#FF9130] z-10"
              style={{ left: "75%" }}
              title="75% minimum threshold"
            />

            {/* 90% threshold marker */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-[#A88BFF] z-10"
              style={{ left: "90%" }}
              title="90% goal threshold"
            />
          </div>

          <div className="relative w-full text-[10px] text-[#CFC6A9] mt-1 flex justify-between">
            <span>0%</span>
            <span className="text-[#FF9130] absolute" style={{ left: "75%", transform: "translateX(-50%)" }}>
              75%
            </span>
            <span className="text-[#A88BFF] absolute" style={{ left: "90%", transform: "translateX(-50%)" }}>
              90%
            </span>
            <span>100%</span>
          </div>
        </div>

        {/* Plain Recovery Plan */}
        <div className="bg-[#0B0E1F]/70 border border-[rgba(241,233,210,0.08)] p-2.5 rounded text-xs mb-3 font-mono">
          <div className="text-[#F1E9D2] font-semibold">
            {subject.required75 !== null ? (
              <span>
                Need <strong className="text-[#FFB35C]">{subject.required75}</strong> of{" "}
                <strong>{subject.remaining}</strong> left · Can miss{" "}
                <strong className={subject.safeAbsences75 !== null && subject.safeAbsences75 > 0 ? "text-[#6FA043]" : "text-[#FF9130]"}>
                  {subject.safeAbsences75 ?? 0}
                </strong>
              </span>
            ) : (
              <span className="text-[#E33D2E]">Detention mathematically unavoidable (0/75% room)</span>
            )}
          </div>
        </div>

        {/* Plain English Explanation */}
        <p className="text-xs text-[#CFC6A9] leading-relaxed mb-2">
          {subject.explanation75}
        </p>

        {/* Future Gap Alternative ("otherGap") */}
        {isFuture && subject.otherGap && (
          <div className="text-[11px] bg-[#1C2448]/50 border border-[rgba(241,233,210,0.08)] p-2 rounded text-[#FFB35C] mt-2 mb-2">
            <strong>Alternate gap policy:</strong> If you miss classes until {planningDate}:{" "}
            {UI_STATUS[subject.otherGap.detention]} (need {subject.otherGap.required75 ?? "all"} of {subject.remaining})
          </div>
        )}

        {/* Warnings / Percentage mode note */}
        {subject.warnings && subject.warnings.length > 0 && (
          <div className="text-[11px] text-[#FF9130] flex items-center gap-1.5 mt-2">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            <span>{subject.warnings.join("; ")}</span>
          </div>
        )}
      </div>

      {/* 90% Goal Disclosure */}
      <div className="border-t border-[rgba(241,233,210,0.08)] pt-2.5 mt-2">
        <button
          onClick={() => setShowGoal90(!showGoal90)}
          className="text-xs text-[#A88BFF] hover:text-[#FFB35C] flex items-center justify-between w-full font-medium"
        >
          <span>90% Goal Guidance</span>
          {showGoal90 ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showGoal90 && (
          <p className="text-xs text-[#CFC6A9] mt-2 bg-[#1C2448]/40 p-2.5 rounded border border-[#7C4DFF]/20">
            {subject.explanation90}
          </p>
        )}
      </div>
    </div>
  );
}
