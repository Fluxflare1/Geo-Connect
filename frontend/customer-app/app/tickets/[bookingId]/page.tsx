"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import { useRequireAuth } from "@/lib/auth-context";
import type { Booking, Ticket } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { QRCode } from "qrcode.react";

export default function TicketsPage() {
  const { checking } = useRequireAuth();

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600">
        Checking your session…
      </div>
    );
  }

  const params = useParams<{ bookingId: string }>();
  const router = useRouter();
  const bookingId = params.bookingId;

  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadBooking() {
      setLoading(true);
      setError(null);
      try {
        const data = await apiFetch<Booking>(`/bookings/${bookingId}`);
        setBooking(data);
      } catch (err: any) {
        setError(err.message || "Failed to load tickets.");
      } finally {
        setLoading(false);
      }
    }

    if (!bookingId) {
      router.push("/bookings");
      return;
    }

    if (!checking) {
      loadBooking();
    }
  }, [bookingId, router, checking]);

  return (
    <div className="mt-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">Tickets</h1>
        <Button
          type="button"
          variant="secondary"
          onClick={() => router.push(`/bookings/${bookingId}`)}
        >
          Back to booking
        </Button>
      </div>

      {loading && (
        <p className="text-sm text-gray-600">Loading tickets…</p>
      )}

      {error && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 mb-4">
          {error}
        </div>
      )}

      {booking && booking.tickets.length === 0 && (
        <p className="text-sm text-gray-600">
          No tickets found for this booking yet.
        </p>
      )}

      {booking && booking.tickets.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {booking.tickets.map(ticket => (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TicketCard({ ticket }: { ticket: Ticket }) {
  return (
    <div className="bg-white border rounded-lg shadow-sm p-4 flex flex-col items-center">
      <div className="mb-2 text-xs text-gray-500">
        Ticket code:
      </div>
      <div className="font-mono text-sm mb-2">{ticket.ticket_code}</div>

      <div className="mb-3">
        <QRCode
          value={ticket.qr_payload}
          size={180}
          level="M"
          includeMargin
        />
      </div>

      <div className="text-xs text-gray-500">
        Status:{" "}
        <span className="font-semibold">{ticket.status}</span>
      </div>
      {ticket.valid_from && (
        <div className="text-[11px] text-gray-500">
          Valid from: {new Date(ticket.valid_from).toLocaleString()}
        </div>
      )}
      {ticket.valid_until && (
        <div className="text-[11px] text-gray-500">
          Valid until: {new Date(ticket.valid_until).toLocaleString()}
        </div>
      )}
    </div>
  );
}
