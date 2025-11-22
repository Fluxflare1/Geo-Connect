"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { requestPasswordReset } from "@/lib/auth";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [debugToken, setDebugToken] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setDebugToken(null);

    setSubmitting(true);
    try {
      const res = await requestPasswordReset(email);
      setSuccessMessage(res.detail);
      if (res.debug_token) {
        setDebugToken(res.debug_token);
      }
    } catch (err: any) {
      setError(err.message || "Failed to request password reset.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-10 bg-white rounded-lg shadow-sm p-6">
      <h1 className="text-2xl font-semibold mb-4">Forgot password</h1>
      <p className="text-sm text-gray-600 mb-4">
        Enter the email address associated with your account. If it exists, we&apos;ll
        send you a link to reset your password.
      </p>

      {error && (
        <div className="mb-3">
          <Alert variant="error" title="Request failed">
            {error}
          </Alert>
        </div>
      )}

      {successMessage && (
        <div className="mb-3">
          <Alert variant="success" title="Email sent">
            {successMessage}
          </Alert>
        </div>
      )}

      {debugToken && (
        <div className="mb-3">
          <Alert variant="warning" title="Development token (DEBUG mode)">
            <div className="font-mono break-all text-xs">{debugToken}</div>
            <button
              type="button"
              className="mt-1 underline text-xs"
              onClick={() =>
                router.push(`/reset-password?token=${encodeURIComponent(debugToken)}`)
              }
            >
              Go to reset page with this token
            </button>
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

        <Button
          type="submit"
          variant="primary"
          className="w-full flex items-center justify-center gap-2"
          disabled={submitting}
        >
          {submitting && <Spinner size="sm" />}
          <span>{submitting ? "Sending…" : "Send reset link"}</span>
        </Button>
      </form>

      <div className="mt-4 text-xs text-gray-600">
        Remember your password?{" "}
        <button
          type="button"
          className="text-blue-600 underline"
          onClick={() => router.push("/login")}
        >
          Go back to login
        </button>
      </div>
    </div>
  );
}
