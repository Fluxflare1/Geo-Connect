"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import type { Booking, Passenger, Ticket } from "@/lib/types";
import { Button } from "@/components/ui/button";

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

  const bookingId = params.bookingId;

  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelSubmitting, setCancelSubmitting] = useState(false);
  const [cancelError, setCancelError] = useState<string | null>(null);

  useEffect(() => {
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

    if (!bookingId) {
      router.push("/bookings");
      return;
    }

    loadBooking();
  }, [bookingId, router]);

  async function handleCancel() {
    if (!booking) return;
    setCancelSubmitting(true);
    setCancelError(null);
    try {
      await apiFetch(`/bookings/${booking.id}/cancel`, {
        method: "POST",
        body: JSON.stringify({ reason: "CUSTOMER_REQUEST" })
      });
      // Refresh booking
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

          {/* Passengers */}
          <div className="bg-white border rounded-lg shadow-sm p-4 mb-4">
            <h2 className="text-sm font-semibold mb-3">Passengers</h2>
            <div className="space-y-2">
              {booking.passengers.map(p => (
                <div
                  key={p.id}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between border rounded-md px-3 py-2 text-sm"
                >
                  <div>
                    <div className="font-medium">
                      {p.first_name} {p.last_name}
                    </div>
                    <div className="text-xs text-gray-500">
                      Type: {p.passenger_type}
                    </div>
                  </div>
                  <div className="mt-1 sm:mt-0 text-xs text-gray-500">
                    {p.email && <div>Email: {p.email}</div>}
                    {p.phone && <div>Phone: {p.phone}</div>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tickets */}
          <div className="bg-white border rounded-lg shadow-sm p-4 mb-4">
            <h2 className="text-sm font-semibold mb-3">Tickets</h2>
            {booking.tickets.length === 0 ? (
              <p className="text-xs text-gray-600">
                Tickets will appear here after payment is confirmed.
              </p>
            ) : (
              <div className="space-y-2 text-sm">
                {booking.tickets.map(t => (
                  <div
                    key={t.id}
                    className="border rounded-md px-3 py-2 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1"
                  >
                    <div>
                      <div className="text-xs text-gray-500">
                        Ticket code:
                      </div>
                      <div className="font-mono text-sm">{t.ticket_code}</div>
                    </div>
                    <div className="text-xs text-gray-500">
                      Status:{" "}
                      <span className="font-semibold">{t.status}</span>
                    </div>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="primary"
                  className="mt-2"
                  onClick={handleViewTickets}
                >
                  View tickets / QR codes
                </Button>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-2 justify-end">
            {cancelError && (
              <div className="w-full rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
                {cancelError}
              </div>
            )}
            {booking.status === "CONFIRMED" && (
              <Button
                type="button"
                variant="secondary"
                onClick={handleCancel}
                disabled={cancelSubmitting}
              >
                {cancelSubmitting ? "Cancelling…" : "Request cancellation"}
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
