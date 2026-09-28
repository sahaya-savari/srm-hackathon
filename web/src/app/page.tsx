import Link from "next/link";
import { getSections } from "@/lib/data";
import { SEMESTER_START, SEMESTER_END } from "@/lib/calendar";

export default function Home() {
  const sections = getSections();
  const totalSubjects = sections.reduce((acc, s) => acc + s.subjects.length, 0);

  // Calculate semester day metrics (Aug 29 to Nov 29 = 92 days)
  const start = new Date(SEMESTER_START).getTime();
  const end = new Date(SEMESTER_END).getTime();
  const totalDays = Math.round((end - start) / (1000 * 60 * 60 * 24));

  return (
    <div className="flex flex-col min-h-full">
      {/* Hero Section */}
      <section className="py-16 sm:py-24 px-4 text-center max-w-[1000px] mx-auto space-y-6">
        <div className="inline-block bg-[#141A35] border border-[#FF9130]/40 text-[#FFB35C] px-3.5 py-1 text-xs font-semibold uppercase tracking-wider rounded-sm shadow-[2px_2px_0_0_rgba(0,0,0,0.5)]">
          VibeCraft 2026 · Round 1 &quot;The Overworld&quot;
        </div>

        <h1 className="font-['Press_Start_2P'] text-2xl sm:text-4xl lg:text-5xl text-[#F1E9D2] leading-tight sm:leading-relaxed">
          Will you make <span className="text-[#FF9130]">75%</span>?
        </h1>

        <p className="text-sm sm:text-lg text-[#CFC6A9] max-w-2xl mx-auto leading-relaxed">
          Pick your class section, enter your attendance percentage, and see{" "}
          <strong className="text-[#F1E9D2]">exactly how many classes you can miss</strong> before 29 Nov 2026.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <Link
            href="/planner"
            className="btn-block text-sm sm:text-base font-bold uppercase tracking-wider inline-flex items-center gap-2"
          >
            <span>Check my attendance</span>
            <span>→</span>
          </Link>

          <Link
            href="/timetable"
            className="px-5 py-3 bg-[#141A35] text-[#F1E9D2] border border-[rgba(241,233,210,0.2)] text-sm font-semibold rounded-sm hover:border-[#FF9130] transition-colors shadow-[3px_3px_0_0_rgba(0,0,0,0.5)]"
          >
            View Timetables
          </Link>
        </div>
      </section>

      {/* Live Stats Strip */}
      <section className="border-y border-[rgba(241,233,210,0.12)] bg-[#141A35]/60 py-6 px-4">
        <div className="max-w-[1120px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-3">
            <span className="block font-mono text-2xl sm:text-3xl font-extrabold text-[#F1E9D2]">
              {sections.length}
            </span>
            <span className="text-xs uppercase tracking-wider text-[#CFC6A9]">
              Class Sections
            </span>
          </div>
          <div className="p-3">
            <span className="block font-mono text-2xl sm:text-3xl font-extrabold text-[#F1E9D2]">
              {totalSubjects}
            </span>
            <span className="text-xs uppercase tracking-wider text-[#CFC6A9]">
              Subject Timetables
            </span>
          </div>
          <div className="p-3">
            <span className="block font-mono text-2xl sm:text-3xl font-extrabold text-[#6FA043]">
              {totalDays}
            </span>
            <span className="text-xs uppercase tracking-wider text-[#CFC6A9]">
              Semester Days
            </span>
          </div>
          <div className="p-3">
            <span className="block font-mono text-2xl sm:text-3xl font-extrabold text-[#A88BFF]">
              100%
            </span>
            <span className="text-xs uppercase tracking-wider text-[#CFC6A9]">
              Deterministic Math
            </span>
          </div>
        </div>
      </section>

      {/* 3 Step Explainer */}
      <section className="py-16 px-4 max-w-[1120px] mx-auto space-y-10">
        <div className="text-center space-y-2">
          <h2 className="font-['Press_Start_2P'] text-base sm:text-lg text-[#F1E9D2]">
            HOW IT WORKS
          </h2>
          <p className="text-xs text-[#CFC6A9]">
            A decision engine that eliminates guesswork before detention becomes unavoidable.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-6 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] space-y-3">
            <div className="w-8 h-8 rounded-sm bg-[#FF9130] text-[#1B140C] font-bold text-sm flex items-center justify-center font-mono">
              1
            </div>
            <h3 className="font-bold text-base text-[#F1E9D2]">Pick your section</h3>
            <p className="text-xs text-[#CFC6A9] leading-relaxed">
              Select your department &amp; class year from the 13 verified institutional timetables. Real scheduled periods, not estimates.
            </p>
          </div>

          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-6 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] space-y-3">
            <div className="w-8 h-8 rounded-sm bg-[#A88BFF] text-[#1B140C] font-bold text-sm flex items-center justify-center font-mono">
              2
            </div>
            <h3 className="font-bold text-base text-[#F1E9D2]">Enter attendance</h3>
            <p className="text-xs text-[#CFC6A9] leading-relaxed">
              Input percentage (e.g. 68%) or switch to exact attended/held counts. The engine uses integer arithmetic with conservative lower-bound estimation.
            </p>
          </div>

          <div className="bg-[#141A35] border border-[rgba(241,233,210,0.12)] p-6 rounded-sm shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] space-y-3">
            <div className="w-8 h-8 rounded-sm bg-[#6FA043] text-[#1B140C] font-bold text-sm flex items-center justify-center font-mono">
              3
            </div>
            <h3 className="font-bold text-base text-[#F1E9D2]">Get your plan</h3>
            <p className="text-xs text-[#CFC6A9] leading-relaxed">
              Instantly see your required classes for 75% and 90%, safe absence budget, and early warning before irreversible detention occurs.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
