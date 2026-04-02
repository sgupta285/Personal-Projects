export interface CompletionEvent {
  completedAt: string;
}

export interface NotificationRecommendationInput {
  completionHistory: CompletionEvent[];
  quietWindowStart: string;
  quietWindowEnd: string;
}

function clampHour(hour: number): number {
  return Math.min(23, Math.max(0, hour));
}

export function recommendReminderTime(input: NotificationRecommendationInput): string {
  if (input.completionHistory.length === 0) {
    return input.quietWindowStart;
  }

  const hourWeights = input.completionHistory.reduce<Record<number, number>>((accumulator, event) => {
    const hour = new Date(event.completedAt).getUTCHours();
    accumulator[hour] = (accumulator[hour] ?? 0) + 1;
    return accumulator;
  }, {});

  const bestHour = Object.entries(hourWeights)
    .sort((left, right) => Number(right[1]) - Number(left[1]))[0]?.[0];

  const targetHour = clampHour(Number(bestHour ?? 9) - 1);
  const recommended = `${String(targetHour).padStart(2, "0")}:00`;

  if (recommended < input.quietWindowStart) {
    return input.quietWindowStart;
  }
  if (recommended > input.quietWindowEnd) {
    return input.quietWindowEnd;
  }

  return recommended;
}

export function buildFcmPayload(deviceToken: string, title: string, body: string, metadata: Record<string, string>) {
  return {
    to: deviceToken,
    notification: { title, body },
    data: metadata
  };
}
