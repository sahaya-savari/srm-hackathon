import React from "react";
import { StatusChip } from "@/components/ui/StatusChip";
import { Goal90Badge } from "@/components/ui/Goal90Badge";
import type { UiStatus, SubjectPlan, Goal90Status } from "@/lib/attendance";

interface StatusBannerProps {
  overallStatus: UiStatus;
  overall: SubjectPlan;
  planningDate: string;
  today: string;
}

export function StatusBanner({ overallStatus, overall, planningDate, today }: StatusBannerProps) {
  const isFuturePlan = planningDate > today;
  const currentPctStr = overall.currentPct !== null ? `${overall.currentPct.toFixed(2)}%` : "—";
  const planPctStr = overall.pctAtPlanningDate !== null ? `${overall.pctAtPlanningDate.toFixed(2)}%` : "—";

  return (
    <div className="bg-[#141A35] border-2 border-[rgba(241,233,210,0.15)] rounded-sm p-4 sm:p-5 shadow-[5px_5px_0_0_rgba(0,0,0,0.5)] mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-wrap">
          <StatusChip status={overallStatus} size="lg" />
          <Goal90Badge
            status={overall.goal90 as Goal90Status}
            maxPossible={overall.maxPossible}
            required={overall.required90}
            remaining={overall.remaining}
          />
        </div>

        <div className="flex items-center gap-6 text-sm">
          <div>
            <span className="text-xs text-[#CFC6A9] block uppercase tracking-wider">Current Attendance</span>
            <span className="text-xl sm:text-2xl font-bold font-mono text-[#F1E9D2]">
              {currentPctStr}
            </span>
          </div>

          {isFuturePlan && (
            <div className="border-l border-[rgba(241,233,210,0.15)] pl-6">
              <span className="text-xs text-[#CFC6A9] block uppercase tracking-wider">At Planning Date</span>
              <span className="text-xl sm:text-2xl font-bold font-mono text-[#FFB35C]">
                {planPctStr}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
