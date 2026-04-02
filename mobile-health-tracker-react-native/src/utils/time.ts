export function nowIso(): string {
  return new Date().toISOString();
}

export function humanDate(value: string): string {
  return new Date(value).toLocaleDateString();
}
