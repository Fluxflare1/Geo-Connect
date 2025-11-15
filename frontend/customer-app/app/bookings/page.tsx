"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import type { Booking } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { useRequireAuth } from "@/lib/use-require-auth";

function formatDateTime(iso: string | null) {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function BookingsPage() {
  const router = useRouter();
  const { checking } = useRequireAuth();

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (checking) return;

    async function loadBookings() {
      setLoading(true);
      setError(null);
      try {
        const data = await apiFetch<{ bookings: Booking[] }>("/bookings");
        setBookings(data.bookings || []);
      } catch (err: any) {
        setError(err.message || "Failed to load bookings.");
      } finally {
        setLoading(false);
      }
    }

    loadBookings();
  }, [checking]);

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600">
        Checking your session…
      </div>
    );
  }

  return (
    <div className="mt-6">
      <h1 className="text-xl font-semibold mb-3">My bookings</h1>

      {loading && <p className="text-sm text-gray-600">Loading bookings…</p>}

      {error && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 mb-4">
          {error}
        </div>
      )}

      {!loading && !error && bookings.length === 0 && (
        <p className="text-sm text-gray-600">
          You don&apos;t have any bookings yet.
        </p>
      )}

      <div className="space-y-4">
        {bookings.map(b => (
          <div
            key={b.id}
            className="bg-white border rounded-lg shadow-sm p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3"
          >
            <div>
              <div className="text-xs text-gray-500 mb-1">
                Booking ID: <span className="font-mono">{b.id}</span>
              </div>
              <div className="text-sm text-gray-700">
                Status:{" "}
                <span className="font-semibold">{b.status}</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Created: {formatDateTime(b.created_at)}
              </div>
              {b.reservation_expires_at && (
                <div className="text-xs text-gray-500">
                  Reservation expires:{" "}
                  {formatDateTime(b.reservation_expires_at)}
                </div>
              )}
            </div>
            <div className="flex flex-col items-start md:items-end gap-2">
              <div className="text-xs text-gray-500">
                Passengers: {b.passengers.length}
              </div>
              <Button
                variant="primary"
                onClick={() =>
                  router.push(`/bookings/${encodeURIComponent(b.id)}`)
                }
              >
                View details
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
