export const schemaStatements = [
  `CREATE TABLE IF NOT EXISTS workouts (
    id TEXT PRIMARY KEY NOT NULL,
    type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    calories_burned INTEGER NOT NULL,
    notes TEXT,
    date TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    sync_status TEXT NOT NULL
  );`,
  `CREATE TABLE IF NOT EXISTS meals (
    id TEXT PRIMARY KEY NOT NULL,
    meal_type TEXT NOT NULL,
    calories INTEGER NOT NULL,
    protein_grams INTEGER NOT NULL,
    carbs_grams INTEGER NOT NULL,
    fat_grams INTEGER NOT NULL,
    date TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    sync_status TEXT NOT NULL
  );`,
  `CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    target REAL NOT NULL,
    unit TEXT NOT NULL,
    progress REAL NOT NULL,
    deadline TEXT,
    updated_at TEXT NOT NULL,
    sync_status TEXT NOT NULL
  );`
];
