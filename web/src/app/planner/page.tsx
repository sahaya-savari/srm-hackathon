import { Suspense } from "react";
import { Planner } from "@/components/planner/Planner";
import { PlannerSkeleton } from "@/components/planner/PlannerSkeleton";

export const metadata = {
  title: "Planner · Attendance Predictor",
  description: "Calculate how many classes you must attend to stay above 75% or 90% attendance.",
};

export default function PlannerPage() {
  return (
    <Suspense fallback={<PlannerSkeleton />}>
      <Planner />
    </Suspense>
  );
}
