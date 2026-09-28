"use client";

import React from "react";
import { useToday } from "@/lib/useToday";

export function Footer() {
  const today = useToday();

  // Format date nicely if today is available
  let formattedDate = today ? today : "Reading clock...";
  if (today) {
    try {
      const [y, m, d] = today.split("-").map(Number);
      const dt = new Date(y, m - 1, d);
      formattedDate = dt.toLocaleDateString("en-US", {
        weekday: "short",
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    } catch {
      formattedDate = today;
    }
  }

  return (
    <footer className="mt-auto border-t border-[rgba(241,233,210,0.12)] bg-[#141A35] py-6 px-4 text-xs text-[#CFC6A9]">
      <div className="max-w-[1120px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <span className="font-semibold text-[#F1E9D2]">Attendance Predictor</span> · VibeCraft 2026 Round 1
          <p className="text-[11px] text-[#CFC6A9] mt-1">
            Deterministic decision engine based on scheduled occurrences. 1 timetable period = 1 attendance hour.
          </p>
        </div>
        <div className="text-right sm:text-right text-xs">
          <div className="inline-flex items-center gap-2 bg-[#0B0E1F] border border-[rgba(241,233,210,0.12)] px-3 py-1.5 rounded-sm">
            <span className="w-2 h-2 rounded-full bg-[#6FA043]" />
            <span>Today: <strong className="text-[#F1E9D2]">{formattedDate}</strong> (device date)</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
