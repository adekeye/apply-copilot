"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "./AuthProvider";
import { logout } from "@/lib/api";

export function NavBar() {
  const { isAuthed, username } = useAuth();
  const { signOut } = useAuth();
  const router = useRouter();

  function handleLogout() {
    logout();
    signOut();
    router.push("/login");
  }

  return (
    <nav className="nav">
      <strong>Job Application Copilot</strong>
      {isAuthed ? (
        <>
          <Link href="/resume">Resume/Profile</Link>
          <Link href="/jobs">Jobs</Link>
          <span className="small">{username}</span>
          <button onClick={handleLogout}>Logout</button>
        </>
      ) : (
        <>
          <Link href="/login">Login</Link>
          <Link href="/register">Register</Link>
        </>
      )}
    </nav>
  );
}
