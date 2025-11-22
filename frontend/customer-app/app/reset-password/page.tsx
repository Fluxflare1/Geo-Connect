"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { resetPassword } from "@/lib/auth";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialToken = searchParams.get("token") || "";

  const [token, setToken] = useState(initialToken);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (initialToken) {
      setToken(initialToken);
    }
  }, [initialToken]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!token) {
      setError("Reset token is required.");
      return;
    }

    if (!newPassword || !confirmPassword) {
      setError("All fields are required.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("New password and confirmation do not match.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await resetPassword(token, newPassword);
      setSuccessMessage(res.detail);
      setNewPassword("");
      setConfirmPassword("");

      // Optional auto-redirect after success:
      // setTimeout(() => router.push("/login"), 1500);
    } catch (err: any) {
      setError(err.message || "Failed to reset password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-10 bg-white rounded-lg shadow-sm p-6">
      <h1 className="text-2xl font-semibold mb-4">Reset password</h1>
      <p className="text-sm text-gray-600 mb-4">
        Enter your new password. If your reset link or token has expired, please request
        a new one from the Forgot password page.
      </p>

      {error && (
        <div className="mb-3">
          <Alert variant="error" title="Could not reset password">
            {error}
          </Alert>
        </div>
      )}

      {successMessage && (
        <div className="mb-3">
          <Alert variant="success" title="Password updated">
            {successMessage}
          </Alert>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="token">
            Reset token
          </label>
          <input
            id="token"
            type="text"
            required
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
            value={token}
            onChange={e => setToken(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="new-password">
            New password
          </label>
          <input
            id="new-password"
            type="password"
            required
            autoComplete="new-password"
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={newPassword}
            onChange={e => setNewPassword(e.target.value)}
          />
        </div>

        <div>
          <label
            className="block text-sm font-medium mb-1"
            htmlFor="confirm-password"
          >
            Confirm new password
          </label>
          <input
            id="confirm-password"
            type="password"
            required
            autoComplete="new-password"
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={confirmPassword}
            onChange={e => setConfirmPassword(e.target.value)}
          />
        </div>

        <Button
          type="submit"
          variant="primary"
          className="w-full flex items-center justify-center gap-2"
          disabled={submitting}
        >
          {submitting && <Spinner size="sm" />}
          <span>{submitting ? "Resetting…" : "Reset password"}</span>
        </Button>
      </form>

      <div className="mt-4 text-xs text-gray-600">
        Go back to{" "}
        <button
          type="button"
          className="text-blue-600 underline"
          onClick={() => router.push("/forgot-password")}
        >
          Forgot password
        </button>{" "}
        or{" "}
        <button
          type="button"
          className="text-blue-600 underline"
          onClick={() => router.push("/login")}
        >
          Login
        </button>
        .
      </div>
    </div>
  );
}
