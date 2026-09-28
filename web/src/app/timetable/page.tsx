import { Suspense } from "react";
import { TimetableView } from "@/components/timetable/TimetableView";
import { PlannerSkeleton } from "@/components/planner/PlannerSkeleton";

export const metadata = {
  title: "Section Timetables · Attendance Predictor",
  description: "View verified weekly class schedules and semester occurrence counts for all sections.",
};

export default function TimetablePage() {
  return (
    <Suspense fallback={<PlannerSkeleton />}>
      <TimetableView />
    </Suspense>
  );
}
