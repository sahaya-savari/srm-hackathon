import React from "react";
import Link from "next/link";
import { ArrowRight, CheckCircle2, ShieldAlert, Cpu, BookOpen, Clock } from "lucide-react";

export const metadata = {
  title: "Methodology & Engine · Attendance Predictor",
  description: "Mathematical proofs, deterministic integer formulation, and data provenance.",
};

export default function HowItWorksPage() {
  return (
    <div className="max-w-[960px] mx-auto px-4 py-12 space-y-12">
      {/* Hero */}
      <div className="space-y-3 border-b border-[rgba(241,233,210,0.12)] pb-8">
        <div className="inline-block bg-[#141A35] border border-[#A88BFF]/40 text-[#A88BFF] px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider rounded-sm">
          Technical Methodology
        </div>
        <h1 className="font-['Press_Start_2P'] text-xl sm:text-3xl text-[#F1E9D2] leading-tight">
          HOW IT WORKS
        </h1>
        <p className="text-sm sm:text-base text-[#CFC6A9] leading-relaxed">
          The deterministic mathematical formulation behind recovery trajectories, absence budgeting, and irreversible detention alerts.
        </p>
      </div>

      {/* Product Thesis */}
      <div className="bg-[#141A35] border-2 border-[#FF9130] p-6 rounded-sm shadow-[4px_4px_0_0_rgba(0,0,0,0.5)]">
        <span className="text-xs uppercase font-bold tracking-wider text-[#FF9130] block mb-1">
          Core Product Thesis
        </span>
        <blockquote className="text-base sm:text-lg font-medium text-[#F1E9D2] italic leading-relaxed">
          &ldquo;We didn&apos;t build an attendance calculator. We built a decision engine that tells a student exactly how much recovery room they have before detention becomes mathematically unavoidable.&rdquo;
        </blockquote>
      </div>

      {/* 1. The Core Formulas */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-[#FF9130]" />
          <h2 className="font-['Press_Start_2P'] text-sm sm:text-base text-[#F1E9D2]">
            1. Mathematical Formulation
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-[#CFC6A9] leading-relaxed">
          Let <strong className="text-[#F1E9D2]">A</strong> be attended classes so far, <strong className="text-[#F1E9D2]">H</strong> be classes held so far, and <strong className="text-[#F1E9D2]">R</strong> be remaining scheduled classes until 29 Nov 2026. The target threshold is <strong className="text-[#F1E9D2]">T = p/q</strong> (where 75% = 3/4 and 90% = 9/10).
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm space-y-2 font-mono text-xs">
            <span className="text-[#FFB35C] font-bold block font-sans">Required Classes to Attend:</span>
            <div className="bg-[#0B0E1F] p-3 rounded text-[#F1E9D2]">
              x = max(0, ⌈(p × (H + R) − q × A) ÷ q⌉)
            </div>
            <p className="text-[11px] text-[#CFC6A9] font-sans">
              Feasible if and only if x ≤ R. If x &gt; R, reaching the target is impossible.
            </p>
          </div>

          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm space-y-2 font-mono text-xs">
            <span className="text-[#6FA043] font-bold block font-sans">Safe Absence Budget (Slack):</span>
            <div className="bg-[#0B0E1F] p-3 rounded text-[#F1E9D2]">
              safe_absences = R − x
            </div>
            <p className="text-[11px] text-[#CFC6A9] font-sans">
              The number of remaining classes a student can afford to miss while remaining ≥ 75%.
            </p>
          </div>

          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm space-y-2 font-mono text-xs">
            <span className="text-[#A88BFF] font-bold block font-sans">Best Possible Final Attendance:</span>
            <div className="bg-[#0B0E1F] p-3 rounded text-[#F1E9D2]">
              max_possible = (A + R) ÷ (H + R)
            </div>
            <p className="text-[11px] text-[#CFC6A9] font-sans">
              The ceiling reached if every single remaining class is attended.
            </p>
          </div>

          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm space-y-2 font-mono text-xs">
            <span className="text-[#E33D2E] font-bold block font-sans">Irreversible Detention Condition:</span>
            <div className="bg-[#0B0E1F] p-3 rounded text-[#F1E9D2]">
              max_possible &lt; 75.00%  ⟺  x &gt; R
            </div>
            <p className="text-[11px] text-[#CFC6A9] font-sans">
              Mathematically guaranteed detention. Early alert shown with proof.
            </p>
          </div>
        </div>
      </section>

      {/* 2. Floating Point Traps */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-[#FF9130]" />
          <h2 className="font-['Press_Start_2P'] text-sm sm:text-base text-[#F1E9D2]">
            2. Exact Integer Arithmetic vs Floats
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-[#CFC6A9] leading-relaxed">
          Standard IEEE-754 binary floating-point representation suffers from precision artifacts. For example, in JavaScript:
        </p>
        <div className="bg-[#141A35] p-4 rounded-sm border border-[rgba(241,233,210,0.12)] font-mono text-xs text-[#FFB35C]">
          0.55 * 100 === 55.00000000000001
        </div>
        <p className="text-xs sm:text-sm text-[#CFC6A9] leading-relaxed">
          A naive implementation using <code className="text-[#FF9130]">Math.ceil(0.55 * (H + R))</code> would erroneously round up to 56 instead of 55! To guarantee 100% mathematical correctness, our engine uses integer ceiling division:
        </p>
        <div className="bg-[#0B0E1F] p-4 rounded-sm border border-[rgba(241,233,210,0.12)] font-mono text-xs text-[#F1E9D2]">
          ceilDiv(a, b) = -Math.floor(-a / b)  // Exact integer quotient without float drift
        </div>
      </section>

      {/* 3. Percentage Mode Ambiguity */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-[#FF9130]" />
          <h2 className="font-['Press_Start_2P'] text-sm sm:text-base text-[#F1E9D2]">
            3. Why Percentages Are Conservative Estimates
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-[#CFC6A9] leading-relaxed">
          When a student enters a rounded portal percentage (e.g. &ldquo;75%&rdquo;), multiple integer pairs can produce that displayed number: 3/4, 6/8, 12/16, or 15/20.
        </p>
        <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-4 rounded-sm text-xs text-[#CFC6A9] space-y-2">
          <p>
            Our engine cross-checks the entered percentage against the timetable&apos;s scheduled class count to find all valid candidate values, then picks the <strong className="text-[#F1E9D2]">lowest matching attended count</strong>.
          </p>
          <p className="text-[#FFB35C]">
            We never over-promise safety. If 75% could mean 12 or 13 classes attended, we assume 12 to ensure the student never falls short. Students can also toggle &ldquo;Exact counts&rdquo; for absolute certainty.
          </p>
        </div>
      </section>

      {/* 4. Counting Rules & Provenance */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-[#FF9130]" />
          <h2 className="font-['Press_Start_2P'] text-sm sm:text-base text-[#F1E9D2]">
            4. Counting Rules &amp; Data Provenance
          </h2>
        </div>
        <ul className="space-y-2 text-xs sm:text-sm text-[#CFC6A9]">
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#6FA043] shrink-0 mt-0.5" />
            <span><strong>1 Timetable Period = 1 Attendance Hour</strong>: A 2-period lab block counts as 2 discrete attendance hours.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#6FA043] shrink-0 mt-0.5" />
            <span><strong>Instruction Days</strong>: Monday through Friday only. Saturdays and Sundays have zero scheduled classes.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#6FA043] shrink-0 mt-0.5" />
            <span><strong>Scheduled vs Conducted</strong>: Class counts reflect the official timetable grid. Today and future days are counted from the live device clock.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#6FA043] shrink-0 mt-0.5" />
            <span><strong>Data Provenance</strong>: The 10 organiser timetable PDFs were image-only scans. OCR cross-checks achieved only ~44% accuracy on course codes, so all 13 sections were hand-transcribed and visually audited cell-by-cell.</span>
          </li>
        </ul>
      </section>

      {/* Call to action */}
      <div className="pt-6 border-t border-[rgba(241,233,210,0.12)] flex justify-between items-center">
        <Link href="/timetable" className="text-xs text-[#CFC6A9] hover:text-[#FF9130] transition-colors">
          ← View Timetable Grid
        </Link>
        <Link href="/planner" className="btn-block text-xs sm:text-sm font-bold uppercase tracking-wider inline-flex items-center gap-2">
          <span>Go to Planner</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
