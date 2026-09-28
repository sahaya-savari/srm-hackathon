"use client";

import React from "react";
import { Calendar as CalendarIcon, Info } from "lucide-react";
import { SEMESTER_END } from "@/lib/calendar";

interface PlanningDateProps {
  today: string;
  planningDate: string;
  gapPolicy: "attend" | "miss";
  onDateChange: (date: string) => void;
  onPolicyChange: (policy: "attend" | "miss") => void;
  gapClasses: number;
}

export function PlanningDate({
  today,
  planningDate,
  gapPolicy,
  onDateChange,
  onPolicyChange,
  gapClasses,
}: PlanningDateProps) {
  const isFuture = planningDate > today;

  // Format today nicely
  let formattedToday = today;
  try {
    const [y, m, d] = today.split("-").map(Number);
    formattedToday = new Date(y, m - 1, d).toLocaleDateString("en-US", {
      weekday: "short",
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    formattedToday = today;
  }

  // Quick chip options
  // Compute next Monday
  const getNextMonday = () => {
    try {
      const [y, m, d] = today.split("-").map(Number);
      const dt = new Date(y, m - 1, d);
      const day = dt.getDay(); // 0 is Sunday, 1 is Monday
      const daysUntilMonday = ((1 - day + 7) % 7) || 7;
      dt.setDate(dt.getDate() + daysUntilMonday);
      return dt.toISOString().slice(0, 10);
    } catch {
      return today;
    }
  };

  const chips = [
    { label: "Today", date: today },
    { label: "Next Mon", date: getNextMonday() },
    { label: "1 Oct", date: "2026-10-01" },
    { label: "1 Nov", date: "2026-11-01" },
    { label: "End of term", date: SEMESTER_END },
  ];

  return (
    <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 sm:p-5 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[rgba(241,233,210,0.1)] pb-3">
        <div>
          <span className="text-xs uppercase font-bold text-[#CFC6A9] tracking-wider block">
            Planning Date (Lookahead Target)
          </span>
          <span className="text-xs text-[#6FA043] flex items-center gap-1.5 mt-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#6FA043]" />
            Live Device Today: <strong>{formattedToday}</strong>
          </span>
        </div>

        {/* Date Input */}
        <div className="flex items-center gap-2">
          <CalendarIcon className="w-4 h-4 text-[#FF9130]" />
          <input
            type="date"
            min={today}
            max={SEMESTER_END}
            value={planningDate}
            onChange={(e) => onDateChange(e.target.value)}
            className="bg-[#1C2448] text-[#F1E9D2] font-mono border border-[rgba(241,233,210,0.2)] rounded px-3 py-1.5 text-sm focus:outline-none focus:border-[#FF9130]"
          />
        </div>
      </div>

      {/* Quick Chips */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-[#CFC6A9]">Jump to:</span>
        {chips.map((chip) => {
          const isPast = chip.date < today;
          const isSelected = chip.date === planningDate;

          return (
            <button
              key={chip.label}
              type="button"
              disabled={isPast}
              onClick={() => onDateChange(chip.date)}
              className={`text-xs px-2.5 py-1 rounded-sm border transition-colors ${
                isSelected
                  ? "bg-[#FF9130] text-[#1B140C] font-bold border-[#FF9130]"
                  : isPast
                  ? "opacity-35 cursor-not-allowed bg-[#1C2448] text-[#CFC6A9] border-transparent"
                  : "bg-[#1C2448] text-[#F1E9D2] border-[rgba(241,233,210,0.15)] hover:border-[#FF9130]"
              }`}
            >
              {chip.label}
            </button>
          );
        })}
      </div>

      {/* Future Gap Policy Radio */}
      {isFuture && (
        <div className="bg-[#1C2448]/60 p-3.5 rounded border border-[#FF9130]/30 space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#FFB35C]">
            <Info className="w-4 h-4 shrink-0" />
            <span>
              {gapClasses} class{gapClasses === 1 ? "" : "es"} occur between today and {planningDate}.
            </span>
          </div>

          <div className="text-xs text-[#F1E9D2] flex flex-col sm:flex-row gap-3 pt-1">
            <span className="text-[#CFC6A9]">Between now and your planning date:</span>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="gapPolicy"
                value="attend"
                checked={gapPolicy === "attend"}
                onChange={() => onPolicyChange("attend")}
                className="accent-[#FF9130]"
              />
              <span>Attend all classes</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="gapPolicy"
                value="miss"
                checked={gapPolicy === "miss"}
                onChange={() => onPolicyChange("miss")}
                className="accent-[#FF9130]"
              />
              <span>Miss all classes</span>
            </label>
          </div>
        </div>
      )}
    </div>
  );
}
