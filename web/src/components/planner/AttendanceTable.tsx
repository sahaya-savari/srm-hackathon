"use client";

import React, { useState } from "react";
import { AlertCircle, ToggleLeft, ToggleRight } from "lucide-react";

export interface AttendanceRowState {
  code: string;
  name: string;
  weeklyPeriods: number;
  mode: "percent" | "exact";
  percentRaw: string;
  attendedRaw: string;
  heldRaw: string;
  heldEstimate: number;
}

interface AttendanceTableProps {
  rows: AttendanceRowState[];
  onChangeRow: (code: string, updates: Partial<AttendanceRowState>) => void;
  onSetAllPercent: (percent: string) => void;
  onClearAll: () => void;
  errors: Record<string, string>;
}

export function AttendanceTable({
  rows,
  onChangeRow,
  onSetAllPercent,
  onClearAll,
  errors,
}: AttendanceTableProps) {
  const [bulkPercent, setBulkPercent] = useState<string>("75");

  return (
    <div className="space-y-4">
      {/* Bulk Helpers */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-[#141A35] p-3 rounded-sm border border-[rgba(241,233,210,0.1)]">
        <div className="flex items-center gap-2">
          <label htmlFor="bulk-pct-input" className="text-xs text-[#CFC6A9] font-medium">
            Set all subjects to:
          </label>
          <input
            id="bulk-pct-input"
            type="number"
            min="0"
            max="100"
            step="0.01"
            value={bulkPercent}
            onChange={(e) => setBulkPercent(e.target.value)}
            className="w-16 bg-[#1C2448] text-[#F1E9D2] border border-[rgba(241,233,210,0.2)] rounded px-2 py-1 text-xs text-center font-mono focus:outline-none focus:border-[#FF9130]"
          />
          <span className="text-xs text-[#CFC6A9]">%</span>
          <button
            type="button"
            onClick={() => onSetAllPercent(bulkPercent)}
            className="text-xs bg-[#FF9130] text-[#1B140C] font-bold px-2.5 py-1 rounded shadow-sm hover:bg-[#FFB35C] transition-colors"
          >
            Apply
          </button>
        </div>

        <button
          type="button"
          onClick={onClearAll}
          className="text-xs text-[#CFC6A9] hover:text-[#FFB35C] underline underline-offset-2"
        >
          Clear all
        </button>
      </div>

      {/* Rows */}
      <div className="space-y-3">
        {rows.map((row) => {
          const isExact = row.mode === "exact";
          const rowError = errors[row.code];

          return (
            <div
              key={row.code}
              className={`p-3.5 rounded-sm border transition-all ${
                rowError
                  ? "bg-[#E33D2E]/10 border-[#E33D2E]"
                  : "bg-[#141A35] border-[rgba(241,233,210,0.12)] hover:border-[rgba(241,233,210,0.25)]"
              }`}
            >
              {/* Row Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div>
                  <span className="font-semibold text-sm text-[#F1E9D2] block">
                    {row.name}
                  </span>
                  <div className="flex items-center gap-2 text-xs text-[#CFC6A9]">
                    <span className="font-mono">{row.code}</span>
                    <span>· {row.weeklyPeriods} classes/wk</span>
                  </div>
                </div>

                {/* Mode toggle */}
                <button
                  type="button"
                  onClick={() =>
                    onChangeRow(row.code, {
                      mode: isExact ? "percent" : "exact",
                    })
                  }
                  className="flex items-center gap-1.5 text-xs text-[#A88BFF] hover:text-[#FFB35C] transition-colors self-start sm:self-auto"
                >
                  {isExact ? (
                    <>
                      <ToggleRight className="w-4 h-4 text-[#FF9130]" />
                      <span className="text-[#FF9130] font-semibold">Exact counts</span>
                    </>
                  ) : (
                    <>
                      <ToggleLeft className="w-4 h-4 text-[#CFC6A9]" />
                      <span className="text-[#CFC6A9]">Switch to exact counts</span>
                    </>
                  )}
                </button>
              </div>

              {/* Input Fields */}
              <div className="mt-2.5">
                {!isExact ? (
                  <div>
                    <div className="flex items-center gap-2">
                      <div className="relative flex-1 max-w-[160px]">
                        <input
                          type="number"
                          min="0"
                          max="100"
                          step="0.01"
                          inputMode="decimal"
                          placeholder="e.g. 75"
                          value={row.percentRaw}
                          onChange={(e) =>
                            onChangeRow(row.code, { percentRaw: e.target.value })
                          }
                          className={`w-full bg-[#1C2448] text-[#F1E9D2] font-mono border rounded px-3 py-1.5 text-sm focus:outline-none ${
                            rowError
                              ? "border-[#E33D2E] focus:border-[#E33D2E]"
                              : "border-[rgba(241,233,210,0.2)] focus:border-[#FF9130]"
                          }`}
                        />
                        <span className="absolute right-3 top-2 text-xs text-[#CFC6A9]">
                          %
                        </span>
                      </div>

                      <span className="text-xs text-[#CFC6A9]">
                        Timetable estimate: ~{row.heldEstimate} classes held so far
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="flex items-center gap-1.5">
                      <label className="text-xs text-[#CFC6A9]">Attended:</label>
                      <input
                        type="number"
                        min="0"
                        placeholder="0"
                        value={row.attendedRaw}
                        onChange={(e) =>
                          onChangeRow(row.code, { attendedRaw: e.target.value })
                        }
                        className={`w-20 bg-[#1C2448] text-[#F1E9D2] font-mono border rounded px-2.5 py-1.5 text-sm focus:outline-none ${
                          rowError
                            ? "border-[#E33D2E] focus:border-[#E33D2E]"
                            : "border-[rgba(241,233,210,0.2)] focus:border-[#FF9130]"
                        }`}
                      />
                    </div>

                    <div className="flex items-center gap-1.5">
                      <label className="text-xs text-[#CFC6A9]">Held:</label>
                      <input
                        type="number"
                        min="0"
                        placeholder="0"
                        value={row.heldRaw}
                        onChange={(e) =>
                          onChangeRow(row.code, { heldRaw: e.target.value })
                        }
                        className={`w-20 bg-[#1C2448] text-[#F1E9D2] font-mono border rounded px-2.5 py-1.5 text-sm focus:outline-none ${
                          rowError
                            ? "border-[#E33D2E] focus:border-[#E33D2E]"
                            : "border-[rgba(241,233,210,0.2)] focus:border-[#FF9130]"
                        }`}
                      />
                    </div>

                    <span className="text-xs text-[#CFC6A9]">
                      (Scheduled held: ~{row.heldEstimate})
                    </span>
                  </div>
                )}

                {/* Row validation error */}
                {rowError && (
                  <div className="flex items-center gap-1.5 mt-2 text-xs text-[#E33D2E]">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    <span>{rowError}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
