import React from "react";
import { ShieldCheck, AlertTriangle, AlertOctagon, HelpCircle } from "lucide-react";
import type { UiStatus } from "@/lib/attendance";

interface StatusChipProps {
  status: UiStatus;
  size?: "sm" | "md" | "lg";
}

export function StatusChip({ status, size = "md" }: StatusChipProps) {
  const configs: Record<UiStatus, { bg: string; text: string; border: string; icon: React.ReactNode; label: string }> = {
    SAFE: {
      bg: "bg-[#4C7A2E]/20",
      text: "text-[#6FA043]",
      border: "border-[#6FA043]",
      icon: <ShieldCheck className={size === "lg" ? "w-5 h-5" : "w-4 h-4"} />,
      label: "SAFE",
    },
    "AT RISK": {
      bg: "bg-[#FF9130]/20",
      text: "text-[#FF9130]",
      border: "border-[#FF9130]",
      icon: <AlertTriangle className={size === "lg" ? "w-5 h-5" : "w-4 h-4"} />,
      label: "AT RISK",
    },
    "IRREVERSIBLE DETENTION": {
      bg: "bg-[#E33D2E]/25",
      text: "text-[#E33D2E]",
      border: "border-[#E33D2E]",
      icon: <AlertOctagon className={size === "lg" ? "w-5 h-5" : "w-4 h-4"} />,
      label: "IRREVERSIBLE DETENTION",
    },
    "NO DATA": {
      bg: "bg-[#1C2448]",
      text: "text-[#CFC6A9]",
      border: "border-[rgba(241,233,210,0.2)]",
      icon: <HelpCircle className={size === "lg" ? "w-5 h-5" : "w-4 h-4"} />,
      label: "NO DATA",
    },
  };

  const c = configs[status] || configs["AT RISK"];
  const sizeClasses = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
    lg: "px-3.5 py-1.5 text-sm",
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-bold uppercase rounded-sm border ${c.bg} ${c.text} ${c.border} ${sizeClasses}`}
    >
      {c.icon}
      <span>{c.label}</span>
    </span>
  );
}
