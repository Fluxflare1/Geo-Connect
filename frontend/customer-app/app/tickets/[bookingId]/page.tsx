"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useRequireAuth } from "@/lib/use-require-auth";
import { apiFetch } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import type { TicketDetail } from "@/lib/types";

interface TicketsResponse {
  booking_reference: string;
  provider_name: string;
  origin_name: string;
  destination_name: string;
  departure_time: string;
  tickets: TicketDetail[];
}

function formatDateTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function TicketsPage() {
  const { bookingId } = useParams<{ bookingId: string }>();
  const router = useRouter();
  const { checking } = useRequireAuth();

  const [data, setData] = useState<TicketsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (checking) return;

    async function loadTickets() {
      if (!bookingId) {
        router.push("/bookings");
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const resp = await apiFetch<TicketsResponse>(
          `/tickets/${encodeURIComponent(bookingId)}`
        );
        setData(resp);
      } catch (err: any) {
        setError(err.message || "Failed to load tickets.");
      } finally {
        setLoading(false);
      }
    }

    loadTickets();
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

      <h1 className="text-xl font-semibold mb-3">Your tickets</h1>

      {loading && (
        <p className="text-sm text-gray-600 flex items-center gap-2">
          <Spinner size="sm" />
          <span>Loading tickets…</span>
        </p>
      )}

      {error && (
        <div className="mb-4">
          <Alert variant="error" title="Could not load tickets">
            {error}
          </Alert>
        </div>
      )}

      {data && !loading && (
        <>
          <div className="bg-white border rounded-lg shadow-sm p-4 mb-4 text-sm">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-500">Booking reference</div>
                <div className="font-mono text-xs">
                  {data.booking_reference}
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Provider</div>
                <div className="font-medium">{data.provider_name}</div>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <div className="text-xs text-gray-500">From</div>
                <div className="font-medium">{data.origin_name}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">To</div>
                <div className="font-medium">{data.destination_name}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Departure</div>
                <div className="font-medium">
                  {formatDateTime(data.departure_time)}
                </div>
              </div>
            </div>
          </div>

          {data.tickets.length === 0 && (
            <Alert variant="warning" title="No tickets found">
              This booking does not have any tickets yet. If you recently paid,
              please check back in a moment or contact support if the issue
              persists.
            </Alert>
          )}

          {data.tickets.length > 0 && (
            <div className="space-y-3">
              {data.tickets.map(t => (
                <div
                  key={t.id}
                  className="bg-white border rounded-lg shadow-sm p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-sm"
                >
                  <div>
                    <div className="text-xs text-gray-500">Ticket</div>
                    <div className="font-medium">
                      {t.ticket_number || t.id}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Passenger: {t.passenger_name}
                    </div>
                    <div className="text-xs text-gray-500">
                      Seat: {t.seat_label || "General"}
                    </div>
                  </div>
                  <div className="flex flex-col items-start sm:items-end gap-2">
                    <div className="text-xs text-gray-500">
                      Status:{" "}
                      <span className="font-semibold">{t.status}</span>
                    </div>
                    <div className="text-[11px] text-gray-500 max-w-xs break-all">
                      Scan data:{" "}
                      <span className="font-mono">{t.qr_payload}</span>
                    </div>
                    {t.qr_image_url && (
                      <img
                        src={t.qr_image_url}
                        alt="Ticket QR"
                        className="h-20 w-20 border rounded-md"
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-4">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() =>
                router.push(`/bookings/${encodeURIComponent(bookingId)}`)
              }
            >
              View booking details
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
