"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { clearToken, getToken } from "@/lib/auth";

interface AuthContextValue {
  isAuthed: boolean;
  username: string | null;
  signIn: (username: string) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  isAuthed: false,
  username: null,
  signIn: () => {},
  signOut: () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

function parseUsername(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.sub ?? null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (token) setUsername(parseUsername(token));
  }, []);

  const signIn = useCallback((name: string) => {
    setUsername(name);
  }, []);

  const signOut = useCallback(() => {
    clearToken();
    setUsername(null);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthed: username !== null, username, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
