import React from "react";

export function PlannerSkeleton() {
  return (
    <div className="max-w-[1120px] mx-auto px-4 py-8 space-y-6 animate-pulse">
      <div className="h-10 bg-[#141A35] rounded w-64 border border-[rgba(241,233,210,0.1)]" />
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-5 space-y-4">
          <div className="h-32 bg-[#141A35] rounded" />
          <div className="h-64 bg-[#141A35] rounded" />
        </div>
        <div className="lg:col-span-7 space-y-4">
          <div className="h-28 bg-[#141A35] rounded" />
          <div className="grid grid-cols-3 gap-3">
            <div className="h-24 bg-[#141A35] rounded" />
            <div className="h-24 bg-[#141A35] rounded" />
            <div className="h-24 bg-[#141A35] rounded" />
          </div>
          <div className="h-48 bg-[#141A35] rounded" />
        </div>
      </div>
    </div>
  );
}
