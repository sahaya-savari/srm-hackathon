import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-[rgba(241,233,210,0.12)] bg-[#0B0E1F] sticky top-0 z-50">
      <div className="max-w-[1120px] mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 bg-[#FF9130] flex items-center justify-center font-bold text-[#1B140C] text-sm shadow-[2px_2px_0_0_rgba(0,0,0,0.5)]">
            AP
          </div>
          <div>
            <span className="font-['Press_Start_2P'] text-[11px] sm:text-xs text-[#F1E9D2] tracking-wider group-hover:text-[#FF9130] transition-colors">
              ATTENDANCE PREDICTOR
            </span>
            <span className="hidden sm:inline-block ml-2 text-[10px] px-1.5 py-0.5 bg-[#1C2448] text-[#A88BFF] rounded border border-[#7C4DFF]/40">
              VibeCraft &apos;26
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-4 sm:gap-6 text-xs sm:text-sm font-medium">
          <Link
            href="/planner"
            className="text-[#F1E9D2] hover:text-[#FF9130] transition-colors py-1 border-b-2 border-transparent hover:border-[#FF9130]"
          >
            Planner
          </Link>
          <Link
            href="/timetable"
            className="text-[#CFC6A9] hover:text-[#FF9130] transition-colors py-1"
          >
            Timetables
          </Link>
          <Link
            href="/how-it-works"
            className="text-[#CFC6A9] hover:text-[#FF9130] transition-colors py-1"
          >
            Methodology
          </Link>
        </nav>
      </div>
    </header>
  );
}
