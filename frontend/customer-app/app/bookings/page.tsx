"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useRequireAuth } from "@/lib/use-require-auth";
import { apiFetch } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import type { BookingSummary } from "@/lib/types";

interface BookingsResponse {
  bookings: BookingSummary[];
}

function formatDateTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function BookingsPage() {
  const router = useRouter();
  const { checking } = useRequireAuth();

  const [bookings, setBookings] = useState<BookingSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (checking) return;

    async function loadBookings() {
      setLoading(true);
      setError(null);
      try {
        const data = await apiFetch<BookingsResponse>("/bookings");
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
      <div className="mt-6 text-sm text-gray-600 flex items-center gap-2">
        <Spinner size="sm" />
        <span>Checking your session…</span>
      </div>
    );
  }

  return (
    <div className="mt-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">My bookings</h1>
      </div>

      {loading && (
        <p className="text-sm text-gray-600 flex items-center gap-2">
          <Spinner size="sm" />
          <span>Loading your bookings…</span>
        </p>
      )}

      {error && (
        <div className="mb-4">
          <Alert variant="error" title="Could not load bookings">
            {error}
          </Alert>
        </div>
      )}

      {!loading && !error && bookings.length === 0 && (
        <p className="text-sm text-gray-600">
          You don&apos;t have any bookings yet.
        </p>
      )}

      {!loading && !error && bookings.length > 0 && (
        <div className="space-y-3">
          {bookings.map(b => (
            <div
              key={b.id}
              className="border rounded-lg bg-white px-3 py-2 text-sm flex flex-col gap-2 md:flex-row md:items-center md:justify-between"
            >
              <div>
                <div className="font-medium">
                  {b.origin_name} → {b.destination_name}
                </div>
                <div className="text-xs text-gray-500">
                  {b.provider_name}
                </div>
                <div className="text-xs text-gray-500">
                  {formatDateTime(b.departure_time)}
                </div>
              </div>
              <div className="flex flex-col items-start md:items-end gap-2">
                <div className="text-xs text-gray-500">
                  Status:{" "}
                  <span className="font-semibold">{b.status}</span>
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() =>
                      router.push(`/bookings/${encodeURIComponent(b.id)}`)
                    }
                  >
                    View booking
                  </Button>
                  {b.has_tickets && (
                    <Button
                      type="button"
                      variant="primary"
                      size="sm"
                      onClick={() =>
                        router.push(
                          `/tickets/${encodeURIComponent(b.id)}`
                        )
                      }
                    >
                      View tickets
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
