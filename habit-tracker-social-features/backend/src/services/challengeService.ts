export interface LeaderboardRow {
  userId: string;
  name: string;
  score: number;
  progress: number;
}

export function leaderboardWithPositions(rows: LeaderboardRow[]) {
  return rows
    .sort((left, right) => right.score - left.score || right.progress - left.progress)
    .map((row, index) => ({
      ...row,
      rank: index + 1
    }));
}
