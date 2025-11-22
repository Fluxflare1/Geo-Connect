"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { loginWithEmailPassword, getCurrentUser } from "@/lib/auth";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/";

  const existingUser =
    typeof window !== "undefined" ? getCurrentUser() : null;

  const [email, setEmail] = useState(existingUser?.email || "");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (existingUser) {
      router.replace(redirectTo);
    }
  }, [existingUser, redirectTo, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await loginWithEmailPassword(email, password);
      router.push(redirectTo);
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (existingUser) {
    return (
      <div className="max-w-md mx-auto mt-10 bg-white rounded-lg shadow-sm p-6 text-sm text-gray-700">
        <div className="flex items-center gap-2">
          <Spinner size="sm" />
          <span>You are already signed in. Redirecting…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto mt-10 bg-white rounded-lg shadow-sm p-6">
      <h1 className="text-2xl font-semibold mb-4">Sign in</h1>
      <p className="text-sm text-gray-600 mb-6">
        Sign in to search, book trips and view your tickets.
      </p>

      {error && (
        <div className="mb-4">
          <Alert variant="error" title="Login failed">
            {error}
          </Alert>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            autoComplete="email"
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            autoComplete="current-password"
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </div>

        <Button
          type="submit"
          variant="primary"
          className="w-full flex items-center justify-center gap-2"
          disabled={submitting}
        >
          {submitting && <Spinner size="sm" />}
          <span>{submitting ? "Signing in..." : "Sign in"}</span>
        </Button>

        <div className="mt-3 text-xs text-gray-600 text-center">
          <button
            type="button"
            className="text-blue-600 underline"
            onClick={() => router.push("/forgot-password")}
          >
            Forgot your password?
          </button>
        </div>
      </form>
    </div>
  );
}
