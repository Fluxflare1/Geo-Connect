"use client";

import { apiFetch } from "./api-client";
import type { LoginResponse, User } from "./types";

export async function loginWithEmailPassword(email: string, password: string) {
  const data = await apiFetch<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });

  if (typeof window !== "undefined") {
    window.localStorage.setItem("gc_access_token", data.access);
    window.localStorage.setItem("gc_refresh_token", data.refresh);
    window.localStorage.setItem("gc_user", JSON.stringify(data.user));
  }

  return data.user;
}

export function getCurrentUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem("gc_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function logout() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("gc_access_token");
  window.localStorage.removeItem("gc_refresh_token");
  window.localStorage.removeItem("gc_user");
}
