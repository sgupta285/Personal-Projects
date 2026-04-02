import cors from "cors";
import express from "express";
import helmet from "helmet";
import morgan from "morgan";
import { authRouter } from "./routes/auth.js";
import { challengesRouter } from "./routes/challenges.js";
import { habitsRouter } from "./routes/habits.js";
import { healthRouter } from "./routes/health.js";
import { notificationsRouter } from "./routes/notifications.js";
import { usersRouter } from "./routes/users.js";
import { errorMiddleware } from "./middleware/error.js";

export const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

app.get("/", (_request, response) => {
  response.json({
    name: "habit-social-backend",
    docs: {
      login: "POST /auth/login",
      profile: "GET /users/me",
      habits: "POST /habits",
      challenges: "GET /challenges"
    }
  });
});

app.use("/health", healthRouter);
app.use("/auth", authRouter);
app.use("/users", usersRouter);
app.use("/habits", habitsRouter);
app.use("/challenges", challengesRouter);
app.use("/notifications", notificationsRouter);

app.use(errorMiddleware);
