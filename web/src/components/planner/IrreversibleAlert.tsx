import React from "react";
import { AlertOctagon } from "lucide-react";
import type { SubjectPlan } from "@/lib/attendance";

interface IrreversibleAlertProps {
  subjects: SubjectPlan[];
}

export function IrreversibleAlert({ subjects }: IrreversibleAlertProps) {
  const irreversibleSubjects = subjects.filter((s) => s.detention === "IRREVERSIBLE");

  if (irreversibleSubjects.length === 0) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="alert-irreversible bg-[#E33D2E] text-[#F1E9D2] p-5 sm:p-6 rounded-sm border-2 border-[#F1E9D2] shadow-[5px_5px_0_0_rgba(0,0,0,0.6)] mb-6"
    >
      <div className="flex items-start gap-3">
        <AlertOctagon className="w-7 h-7 text-[#F1E9D2] shrink-0 mt-0.5" />
        <div className="space-y-3 flex-1">
          <div className="font-['Press_Start_2P'] text-sm sm:text-base leading-relaxed tracking-wide text-[#F1E9D2]">
            ⚠ IRREVERSIBLE DETENTION
          </div>
          <p className="text-sm font-medium leading-relaxed">
            Even if you attend <strong>every single remaining class</strong>, you cannot reach 75% in{" "}
            <strong>{irreversibleSubjects.length} subject{irreversibleSubjects.length > 1 ? "s" : ""}</strong> before 29 Nov 2026.
          </p>

          <div className="bg-[#1B140C]/60 border border-[rgba(241,233,210,0.2)] p-3 rounded text-xs space-y-1.5 font-mono">
            <div className="text-[#CFC6A9] text-[11px] uppercase tracking-wider mb-1 font-sans">
              Mathematical Proof:
            </div>
            {irreversibleSubjects.map((s) => {
              const maxStr = s.maxPossible !== null ? s.maxPossible.toFixed(2) : "0.00";
              return (
                <div key={s.code} className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 py-1 border-b border-white/10 last:border-none">
                  <span className="font-semibold text-white">{s.name} ({s.code}):</span>
                  <span className="text-[#FFB35C]">
                    ({s.A} + {s.remaining}) ÷ ({s.H} + {s.remaining}) = <strong className="text-white underline">{maxStr}%</strong> &lt; 75.00%
                  </span>
                </div>
              );
            })}
          </div>

          <div className="bg-[#0B0E1F]/50 p-3 rounded text-xs border border-white/10">
            <strong>Recommended Next Steps:</strong> Talk to your faculty advisor or HOD now regarding institutional condonation, medical leave, or on-duty (OD) regularisation options. Keep attending all classes: your other subjects still count towards semester eligibility.
          </div>
        </div>
      </div>
    </div>
  );
}
