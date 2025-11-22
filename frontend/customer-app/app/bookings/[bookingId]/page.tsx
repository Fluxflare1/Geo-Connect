"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useRequireAuth } from "@/lib/use-require-auth";
import { apiFetch } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import type { BookingDetail } from "@/lib/types";

function formatDateTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function BookingDetailPage() {
  const { bookingId } = useParams<{ bookingId: string }>();
  const router = useRouter();
  const { checking } = useRequireAuth();

  const [booking, setBooking] = useState<BookingDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (checking) return;

    async function loadBooking() {
      if (!bookingId) {
        router.push("/bookings");
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const data = await apiFetch<BookingDetail>(
          `/bookings/${encodeURIComponent(bookingId)}`
        );
        setBooking(data);
      } catch (err: any) {
        setError(err.message || "Failed to load booking.");
      } finally {
        setLoading(false);
      }
    }

    loadBooking();
  }, [bookingId, router, checking]);

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600 flex items-center gap-2">
        <Spinner size="sm" />
        <span>Checking your session…</span>
      </div>
    );
  }

  return (
    <div className="mt-6 max-w-3xl mx-auto">
      <button
        type="button"
        className="text-xs text-gray-500 hover:underline mb-2"
        onClick={() => router.push("/bookings")}
      >
        ← Back to bookings
      </button>

      <h1 className="text-xl font-semibold mb-3">Booking details</h1>

      {loading && (
        <p className="text-sm text-gray-600 flex items-center gap-2">
          <Spinner size="sm" />
          <span>Loading booking…</span>
        </p>
      )}

      {error && (
        <div className="mb-4">
          <Alert variant="error" title="Could not load booking">
            {error}
          </Alert>
        </div>
      )}

      {booking && !loading && (
        <div className="bg-white border rounded-lg shadow-sm p-4 space-y-4 text-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-gray-500">Reference</div>
              <div className="font-mono text-xs">{booking.reference}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">Status</div>
              <div className="font-semibold">{booking.status}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-gray-500">Route</div>
              <div className="font-medium">
                {booking.origin_name} → {booking.destination_name}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Provider</div>
              <div className="font-medium">{booking.provider_name}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Departure</div>
              <div className="font-medium">
                {formatDateTime(booking.departure_time)}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Arrival (est.)</div>
              <div className="font-medium">
                {formatDateTime(booking.arrival_time)}
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-500">Passenger</div>
            <div className="font-medium">
              {booking.passenger_name} • {booking.passenger_email}
            </div>
            {booking.passenger_phone && (
              <div className="text-xs text-gray-600">
                Phone: {booking.passenger_phone}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-gray-500">Seats</div>
              <div className="font-medium">{booking.seats}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Total amount</div>
              <div className="font-semibold">
                {booking.currency} {booking.total_price.toFixed(2)}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mt-2">
            {booking.payment_reference &&
              booking.payment_status !== "PAID" && (
                <Button
                  type="button"
                  variant="primary"
                  size="sm"
                  onClick={() =>
                    router.push(
                      `/payment/${encodeURIComponent(
                        booking.payment_reference
                      )}`
                    )
                  }
                >
                  Complete payment
                </Button>
              )}

            {booking.has_tickets && (
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() =>
                  router.push(`/tickets/${encodeURIComponent(booking.id)}`)
                }
              >
                View tickets
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
