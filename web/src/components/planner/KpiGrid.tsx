import React from "react";
import type { SubjectPlan } from "@/lib/attendance";

interface KpiGridProps {
  classesLeftInSemester: number;
  overall: SubjectPlan;
  atRiskCount: number;
  irreversibleCount: number;
  totalSubjects: number;
  planningDate: string;
}

export function KpiGrid({
  classesLeftInSemester,
  overall,
  atRiskCount,
  irreversibleCount,
  totalSubjects,
  planningDate,
}: KpiGridProps) {
  const req75Text =
    overall.required75 !== null
      ? `${overall.required75} of ${overall.remaining}`
      : "Not possible";

  const req90Text =
    overall.required90 !== null
      ? `${overall.required90} of ${overall.remaining}`
      : "Not possible";

  const atRiskTotal = atRiskCount + irreversibleCount;
  const maxPossibleStr = overall.maxPossible !== null ? `${overall.maxPossible.toFixed(2)}%` : "—";
  const safeAbsences = overall.safeAbsences75 !== null ? overall.safeAbsences75 : "—";
  const isSafePositive = overall.safeAbsences75 !== null && overall.safeAbsences75 > 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3.5 sm:gap-4 mb-8">
      {/* 1. Classes left in semester */}
      <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] flex flex-col justify-between">
        <span className="text-[11px] uppercase tracking-wider text-[#CFC6A9] font-medium block">
          Classes left in semester
        </span>
        <div className="my-2">
          <span className="text-2xl sm:text-3xl font-extrabold font-mono text-[#F1E9D2]">
            {classesLeftInSemester}
          </span>
        </div>
        <span className="text-[11px] text-[#CFC6A9]/80 block">
          Scheduled from {planningDate} to 29 Nov
        </span>
      </div>

      {/* 2. Must attend for 75% */}
      <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] flex flex-col justify-between">
        <span className="text-[11px] uppercase tracking-wider text-[#CFC6A9] font-medium block">
          Must attend to stay above 75%
        </span>
        <div className="my-2">
          <span
            className={`text-2xl sm:text-3xl font-extrabold font-mono ${
              overall.required75 !== null ? "text-[#6FA043]" : "text-[#E33D2E]"
            }`}
          >
            {req75Text}
          </span>
        </div>
        <span className="text-[11px] text-[#CFC6A9]/80 block">
          Minimum classes needed
        </span>
      </div>

      {/* 3. Must attend for 90% */}
      <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] flex flex-col justify-between">
        <span className="text-[11px] uppercase tracking-wider text-[#CFC6A9] font-medium block">
          Must attend for 90%
        </span>
        <div className="my-2">
          <span
            className={`text-2xl sm:text-3xl font-extrabold font-mono ${
              overall.required90 !== null ? "text-[#A88BFF]" : "text-[#CFC6A9]"
            }`}
          >
            {req90Text}
          </span>
        </div>
        <span className="text-[11px] text-[#CFC6A9]/80 block">
          {overall.required90 !== null ? "Goal threshold" : `Max achievable: ${maxPossibleStr}`}
        </span>
      </div>

      {/* 4. Can still miss */}
      <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] flex flex-col justify-between">
        <span className="text-[11px] uppercase tracking-wider text-[#CFC6A9] font-medium block">
          Can still miss (75%)
        </span>
        <div className="my-2">
          <span
            className={`text-2xl sm:text-3xl font-extrabold font-mono ${
              isSafePositive ? "text-[#6FA043]" : "text-[#FF9130]"
            }`}
          >
            {safeAbsences}
          </span>
        </div>
        <span className="text-[11px] text-[#CFC6A9]/80 block">
          Allowed absence budget
        </span>
      </div>

      {/* 5. Best possible final % */}
      <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] flex flex-col justify-between">
        <span className="text-[11px] uppercase tracking-wider text-[#CFC6A9] font-medium block">
          Best possible final %
        </span>
        <div className="my-2">
          <span className="text-2xl sm:text-3xl font-extrabold font-mono text-[#F1E9D2]">
            {maxPossibleStr}
          </span>
        </div>
        <span className="text-[11px] text-[#CFC6A9]/80 block">
          If 100% remaining attended
        </span>
      </div>

      {/* 6. Subjects at risk */}
      <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] flex flex-col justify-between">
        <span className="text-[11px] uppercase tracking-wider text-[#CFC6A9] font-medium block">
          Subjects at risk
        </span>
        <div className="my-2">
          <span
            className={`text-2xl sm:text-3xl font-extrabold font-mono ${
              atRiskTotal > 0 ? "text-[#FF9130]" : "text-[#6FA043]"
            }`}
          >
            {atRiskTotal} of {totalSubjects}
          </span>
        </div>
        <span className="text-[11px] text-[#CFC6A9]/80 block">
          {irreversibleCount > 0 ? `${irreversibleCount} irreversible` : "Eligible for recovery"}
        </span>
      </div>
    </div>
  );
}
