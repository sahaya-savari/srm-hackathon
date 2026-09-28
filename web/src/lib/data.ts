import rawData from "@/data/timetables.json";
import type { TimetableData, Section } from "@/lib/calendar";

export const timetableData = rawData as unknown as TimetableData;

export function getSections(): Section[] {
  return timetableData.sections;
}

export function getSection(id: string): Section | undefined {
  return timetableData.sections.find((s) => s.id === id);
}

export const META = timetableData.meta;
