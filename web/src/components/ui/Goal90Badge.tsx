import React from "react";
import { Target } from "lucide-react";
import type { Goal90Status } from "@/lib/attendance";

interface Goal90BadgeProps {
  status: Goal90Status;
  maxPossible?: number | null;
  required?: number | null;
  remaining?: number;
}

export function Goal90Badge({ status, maxPossible, required, remaining }: Goal90BadgeProps) {
  let label = "90% goal";
  let bg = "bg-[#1C2448]";
  let text = "text-[#CFC6A9]";
  let border = "border-[rgba(241,233,210,0.15)]";

  switch (status) {
    case "LOCKED":
      label = "90% locked in";
      bg = "bg-[#7C4DFF]/25";
      text = "text-[#A88BFF]";
      border = "border-[#7C4DFF]";
      break;
    case "ACHIEVED":
      label = "90% on track";
      bg = "bg-[#7C4DFF]/25";
      text = "text-[#A88BFF]";
      border = "border-[#7C4DFF]";
      break;
    case "RECOVERABLE":
      label = required !== undefined && required !== null && remaining !== undefined ? `90% reachable (need ${required}/${remaining})` : "90% reachable";
      bg = "bg-[#7C4DFF]/15";
      text = "text-[#A88BFF]";
      border = "border-[#7C4DFF]/50";
      break;
    case "IMPOSSIBLE":
      label = maxPossible !== undefined && maxPossible !== null ? `90% impossible (max ${maxPossible.toFixed(2)}%)` : "90% not reachable";
      bg = "bg-[#141A35]";
      text = "text-[#CFC6A9]";
      border = "border-[rgba(241,233,210,0.1)]";
      break;
  }

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium rounded-sm border ${bg} ${text} ${border}`}>
      <Target className="w-3 h-3" />
      <span>{label}</span>
    </span>
  );
}
