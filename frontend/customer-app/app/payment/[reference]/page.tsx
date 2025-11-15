"use client";

import { useEffect, useState } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import type { Booking, PaymentSession } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface StoredPaymentSession extends PaymentSession {}

export default function PaymentPage() {
  const params = useParams<{ reference: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();

  const bookingId = searchParams.get("bookingId");

  const [session, setSession] = useState<StoredPaymentSession | null>(null);
  const [booking, setBooking] = useState<Booking | null>(null);
  const [checkingStatus, setCheckingStatus] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reference = params.reference;

  useEffect(() => {
    if (!bookingId) {
      router.push("/");
      return;
    }

    // Load last payment session from localStorage
    if (typeof window !== "undefined") {
      const raw = window.localStorage.getItem("gc_last_payment_session");
      if (raw) {
        try {
          const parsed = JSON.parse(raw) as StoredPaymentSession;
          if (parsed.payment_reference === reference) {
            setSession(parsed);
          }
        } catch {
          // ignore
        }
      }
    }
  }, [bookingId, reference, router]);

  async function checkBookingStatus() {
    if (!bookingId) return;
    setCheckingStatus(true);
    setError(null);
    try {
      const data = await apiFetch<Booking>(`/bookings/${bookingId}`);
      setBooking(data);
    } catch (err: any) {
      setError(err.message || "Failed to load booking status.");
    } finally {
      setCheckingStatus(false);
    }
  }

  function handleGoToPayment() {
    if (!session) return;
    if (typeof window !== "undefined") {
      window.location.href = session.redirect_url;
    }
  }

  function handleViewBooking() {
    if (!bookingId) return;
    router.push(`/bookings/${encodeURIComponent(bookingId)}`);
  }

  return (
    <div className="max-w-lg mx-auto mt-10 bg-white border rounded-lg shadow-sm p-6">
      <h1 className="text-xl font-semibold mb-3">Complete your payment</h1>

      {!session && (
        <p className="text-sm text-gray-600 mb-4">
          Payment session details not found. If you have already paid, you can
          check your booking status below.
        </p>
      )}

      {session && (
        <div className="mb-6 space-y-2 text-sm">
          <p>
            Provider:{" "}
            <span className="font-medium">{session.provider}</span>
          </p>
          <p>
            Reference:{" "}
            <span className="font-mono">{session.payment_reference}</span>
          </p>
          <p className="text-xs text-gray-500">
            You will be redirected to the payment provider&apos;s page. After
            completing payment, you may be redirected back to this application
            or you can manually return and check your booking status.
          </p>
          <Button
            type="button"
            variant="primary"
            className="mt-2"
            onClick={handleGoToPayment}
          >
            Go to payment
          </Button>
        </div>
      )}

      <hr className="my-4" />

      <div className="space-y-3">
        <h2 className="text-sm font-semibold">Booking status</h2>
        <p className="text-xs text-gray-600">
          After you complete payment, use the button below to refresh the
          booking status.
        </p>

        {error && (
          <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {booking && (
          <div className="rounded-md bg-gray-50 border px-3 py-2 text-sm">
            <p>
              Booking ID:{" "}
              <span className="font-mono">{booking.id}</span>
            </p>
            <p>
              Status:{" "}
              <span className="font-semibold">{booking.status}</span>
            </p>
          </div>
        )}

        <div className="flex gap-2">
          <Button
            type="button"
            variant="secondary"
            onClick={checkBookingStatus}
            disabled={checkingStatus}
          >
            {checkingStatus ? "Checking…" : "Check booking status"}
          </Button>
          <Button
            type="button"
            variant="primary"
            onClick={handleViewBooking}
          >
            View booking
          </Button>
        </div>
      </div>
    </div>
  );
}
