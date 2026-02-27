"use client";

import { FormEvent, useState } from "react";
import { login } from "@/lib/api";

export default function LoginPage() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");
  const [message, setMessage] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      const data = await login(username, password);
      localStorage.setItem("copilot_token", data.access_token);
      setMessage("Logged in. Token saved locally in this browser.");
    } catch (err) {
      setMessage((err as Error).message);
    }
  }

  return (
    <section className="card">
      <h2>App Login</h2>
      <p className="small">This is local app auth only, not job-board auth.</p>
      <form onSubmit={onSubmit}>
        <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button type="submit">Login</button>
      </form>
      {message && <p className="small">{message}</p>}
    </section>
  );
}
