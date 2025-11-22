"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useRequireAuth } from "@/lib/use-require-auth";
import { apiFetch } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";

interface PaymentSession {
  reference: string;
  booking_id: string;
  provider_gateway: string;
  amount: number;
  currency: string;
  status: "PENDING" | "REDIRECTED" | "PAID" | "FAILED" | "EXPIRED";
  checkout_url?: string;
  last_checked_at?: string;
}

export default function PaymentPage() {
  const { reference } = useParams<{ reference: string }>();
  const router = useRouter();
  const { checking } = useRequireAuth();

  const [session, setSession] = useState<PaymentSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingError, setLoadingError] = useState<string | null>(null);
  const [checkingStatus, setCheckingStatus] = useState(false);
  const [statusError, setStatusError] = useState<string | null>(null);

  useEffect(() => {
    if (checking) return;

    async function loadSession() {
      if (!reference) {
        setLoadingError("Missing payment reference.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setLoadingError(null);
      try {
        const data = await apiFetch<PaymentSession>(
          `/payments/session/${encodeURIComponent(reference)}`
        );
        setSession(data);
      } catch (err: any) {
        setLoadingError(err.message || "Failed to load payment session.");
      } finally {
        setLoading(false);
      }
    }

    loadSession();
  }, [checking, reference]);

  async function handleOpenGateway() {
    if (!session?.checkout_url) return;
    window.location.href = session.checkout_url;
  }

  async function handleCheckStatus() {
    if (!reference) return;
    setCheckingStatus(true);
    setStatusError(null);
    try {
      const data = await apiFetch<PaymentSession>(
        `/payments/session/${encodeURIComponent(reference)}/refresh`
      );
      setSession(data);

      if (data.status === "PAID") {
        router.push(`/bookings/${encodeURIComponent(data.booking_id)}`);
      }
    } catch (err: any) {
      setStatusError(err.message || "Failed to refresh payment status.");
    } finally {
      setCheckingStatus(false);
    }
  }

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600 flex items-center gap-2">
        <Spinner size="sm" />
        <span>Checking your session…</span>
      </div>
    );
  }

  return (
    <div className="mt-6 max-w-xl mx-auto bg-white border rounded-lg shadow-sm p-4">
      <h1 className="text-xl font-semibold mb-3">Complete payment</h1>

      {loading && (
        <p className="text-sm text-gray-600 flex items-center gap-2">
          <Spinner size="sm" />
          <span>Loading payment session…</span>
        </p>
      )}

      {loadingError && (
        <Alert variant="error" title="Could not load payment">
          {loadingError}
        </Alert>
      )}

      {session && !loading && (
        <>
          <div className="space-y-3 text-sm mb-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-gray-500">Amount</div>
                <div className="font-semibold">
                  {session.currency} {session.amount.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Gateway</div>
                <div className="font-medium">{session.provider_gateway}</div>
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Status</div>
              <div className="font-medium">{session.status}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Booking</div>
              <button
                type="button"
                className="text-blue-600 underline text-xs"
                onClick={() =>
                  router.push(
                    `/bookings/${encodeURIComponent(session.booking_id)}`
                  )
                }
              >
                View booking details
              </button>
            </div>
          </div>

          {statusError && (
            <div className="mb-3">
              <Alert variant="error" title="Could not refresh status">
                {statusError}
              </Alert>
            </div>
          )}

          <div className="flex flex-col gap-3">
            {session.checkout_url && session.status === "PENDING" && (
              <Button
                type="button"
                variant="primary"
                className="w-full"
                onClick={handleOpenGateway}
              >
                Go to payment page
              </Button>
            )}

            <Button
              type="button"
              variant="secondary"
              className="w-full flex items-center justify-center gap-2"
              disabled={checkingStatus}
              onClick={handleCheckStatus}
            >
              {checkingStatus && <Spinner size="sm" />}
              <span>
                {checkingStatus ? "Checking status…" : "Refresh payment status"}
              </span>
            </Button>

            <button
              type="button"
              className="text-xs text-gray-600 underline"
              onClick={() =>
                router.push(
                  `/bookings/${encodeURIComponent(session.booking_id)}`
                )
              }
            >
              Skip for now and view booking
            </button>
          </div>
        </>
      )}
    </div>
  );
}
