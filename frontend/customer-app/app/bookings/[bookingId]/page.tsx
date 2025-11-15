"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import type { Booking } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { useRequireAuth } from "@/lib/use-require-auth";

function formatDateTime(iso: string | null) {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleString();
}

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: currency || "NGN"
  }).format(amount / 100);
}

export default function BookingDetailPage() {
  const params = useParams<{ bookingId: string }>();
  const router = useRouter();
  const { checking } = useRequireAuth();

  const bookingId = params.bookingId;

  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelSubmitting, setCancelSubmitting] = useState(false);
  const [cancelError, setCancelError] = useState<string | null>(null);

  useEffect(() => {
    if (checking) return;
    if (!bookingId) {
      router.push("/bookings");
      return;
    }

    async function loadBooking() {
      setLoading(true);
      setError(null);
      try {
        const data = await apiFetch<Booking>(`/bookings/${bookingId}`);
        setBooking(data);
      } catch (err: any) {
        setError(err.message || "Failed to load booking.");
      } finally {
        setLoading(false);
      }
    }

    loadBooking();
  }, [bookingId, router, checking]);

  async function handleCancel() {
    if (!booking) return;
    setCancelSubmitting(true);
    setCancelError(null);
    try {
      await apiFetch(`/bookings/${booking.id}/cancel`, {
        method: "POST",
        body: JSON.stringify({ reason: "CUSTOMER_REQUEST" })
      });
      const data = await apiFetch<Booking>(`/bookings/${booking.id}`);
      setBooking(data);
    } catch (err: any) {
      setCancelError(err.message || "Failed to cancel booking.");
    } finally {
      setCancelSubmitting(false);
    }
  }

  function handleViewTickets() {
    if (!booking) return;
    router.push(`/tickets/${encodeURIComponent(booking.id)}`);
  }

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600">
        Checking your session…
      </div>
    );
  }

  return (
    <div className="mt-6 max-w-3xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Booking details</h1>

      {loading && (
        <p className="text-sm text-gray-600">Loading booking details…</p>
      )}

      {error && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 mb-4">
          {error}
        </div>
      )}

      {booking && (
        <>
          {/* existing content unchanged */}
          <div className="bg-white border rounded-lg shadow-sm p-4 mb-4">
            <div className="text-xs text-gray-500 mb-1">
              Booking ID:{" "}
              <span className="font-mono">{booking.id}</span>
            </div>
            <div className="text-sm text-gray-700 mb-1">
              Status:{" "}
              <span className="font-semibold">{booking.status}</span>
            </div>
            <div className="text-xs text-gray-500">
              Created: {formatDateTime(booking.created_at)}
            </div>
            {booking.reservation_expires_at && (
              <div className="text-xs text-gray-500">
                Reservation expires:{" "}
                {formatDateTime(booking.reservation_expires_at)}
              </div>
            )}
            <div className="mt-2 text-sm text-gray-700">
              Total amount:{" "}
              <span className="font-semibold">
                {formatCurrency(booking.total_amount, booking.currency)}
              </span>
            </div>
          </div>

          {/* passengers + tickets + actions (same as before) */}
          {/* ... (use your existing content from previous step) */}
        </>
      )}
    </div>
  );
}
