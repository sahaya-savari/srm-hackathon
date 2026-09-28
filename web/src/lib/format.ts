export function fmtPct(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "—";
  return `${val.toFixed(2)}%`;
}

export function fmtCount(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "—";
  return String(val);
}

export function pluralize(count: number, singular: string, plural: string = `${singular}s`): string {
  return `${count} ${count === 1 ? singular : plural}`;
}
