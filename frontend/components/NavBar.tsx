"use client";

import Link from "next/link";

export function NavBar() {
  return (
    <nav className="nav">
      <strong>Job Application Copilot</strong>
      <Link href="/login">Login</Link>
      <Link href="/resume">Resume/Profile</Link>
      <Link href="/jobs">Jobs</Link>
    </nav>
  );
}
