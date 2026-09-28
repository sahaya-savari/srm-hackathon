"use client";
/**
 * useToday() — today's date (ISO "YYYY-MM-DD") from the user's device, hydration-safe.
 *
 * Returns null during server rendering / static generation and the real local date in the browser,
 * so a build-time date can never be frozen into the page and React never sees a hydration mismatch.
 * Uses useSyncExternalStore instead of setState-in-useEffect (which Next.js 16's ESLint rule
 * react-hooks/set-state-in-effect rejects).
 *
 *   const today = useToday();
 *   if (!today) return <PlannerSkeleton />;
 */
import { useSyncExternalStore } from "react";
import { localTodayISO } from "./calendar";

// Re-render at local midnight so a tab left open overnight rolls over to the new day.
function subscribe(onChange: () => void) {
  const now = new Date();
  const msToMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1).getTime() - now.getTime() + 1000;
  const t = setTimeout(onChange, msToMidnight);
  return () => clearTimeout(t);
}

export function useToday(): string | null {
  return useSyncExternalStore(subscribe, () => localTodayISO(), () => null);
}
