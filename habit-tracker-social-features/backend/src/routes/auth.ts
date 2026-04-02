import { Router } from "express";
import jwt from "jsonwebtoken";
import { z } from "zod";
import { pool } from "../db/index.js";
import { env } from "../config/env.js";

export const authRouter = Router();

const loginSchema = z.object({
  email: z.string().email()
});

authRouter.post("/login", async (request, response, next) => {
  try {
    const payload = loginSchema.parse(request.body);
    const result = await pool.query(
      "select id, email, name from users where email = $1",
      [payload.email]
    );

    if (result.rowCount === 0) {
      response.status(404).json({ error: "User not found" });
      return;
    }

    const user = result.rows[0];
    const token = jwt.sign({ sub: user.id, email: user.email, name: user.name }, env.jwtSecret, { expiresIn: "7d" });

    response.json({ token, user });
  } catch (error) {
    next(error);
  }
});
