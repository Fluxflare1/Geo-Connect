"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import type { SupportTicket } from "@/lib/types";
import { Button } from "@/components/ui/button";

type Category = "BOOKING" | "PAYMENT" | "TRIP" | "ACCOUNT" | "OTHER";
type Priority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

interface TicketsResponse {
  tickets: SupportTicket[];
}

function formatDateTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function SupportPage() {
  const router = useRouter();

  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loadingTickets, setLoadingTickets] = useState(true);
  const [ticketsError, setTicketsError] = useState<string | null>(null);

  const [subject, setSubject] = useState("");
  const [category, setCategory] = useState<Category>("OTHER");
  const [priority, setPriority] = useState<Priority>("MEDIUM");
  const [bookingId, setBookingId] = useState("");
  const [providerId, setProviderId] = useState("");
  const [message, setMessage] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTickets() {
      setLoadingTickets(true);
      setTicketsError(null);
      try {
        const data = await apiFetch<TicketsResponse>("/support/tickets");
        setTickets(data.tickets || []);
      } catch (err: any) {
        setTicketsError(err.message || "Failed to load support tickets.");
      } finally {
        setLoadingTickets(false);
      }
    }

    loadTickets();
  }, []);

  async function handleCreateTicket(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setCreateError(null);

    try {
      const payload: any = {
        subject,
        category,
        priority,
        message
      };
      if (bookingId.trim()) {
        payload.booking_id = bookingId.trim();
      }
      if (providerId.trim()) {
        payload.provider_id = providerId.trim();
      }

      const ticket = await apiFetch("/support/tickets", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      // After creation, reload list & clear form
      const data = await apiFetch<TicketsResponse>("/support/tickets");
      setTickets(data.tickets || []);

      setSubject("");
      setCategory("OTHER");
      setPriority("MEDIUM");
      setBookingId("");
      setProviderId("");
      setMessage("");

      // Navigate to new ticket
      if (ticket && ticket.id) {
        router.push(`/support/${encodeURIComponent(ticket.id)}`);
      }
    } catch (err: any) {
      setCreateError(err.message || "Failed to create support ticket.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="mt-6 max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Support</h1>

      {/* Ticket creation */}
      <div className="bg-white border rounded-lg shadow-sm p-4 mb-6">
        <h2 className="text-sm font-semibold mb-3">Open a new ticket</h2>

        {createError && (
          <div className="mb-3 rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
            {createError}
          </div>
        )}

        <form onSubmit={handleCreateTicket} className="space-y-4">
          <div>
            <label className="block text-xs font-medium mb-1">
              Subject
            </label>
            <input
              type="text"
              required
              value={subject}
              onChange={e => setSubject(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="e.g. Issue with my booking"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={e =>
                  setCategory(e.target.value as Category)
                }
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="BOOKING">Booking</option>
                <option value="PAYMENT">Payment</option>
                <option value="TRIP">Trip</option>
                <option value="ACCOUNT">Account</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">
                Priority
              </label>
              <select
                value={priority}
                onChange={e =>
                  setPriority(e.target.value as Priority)
                }
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">
                Booking ID (optional)
              </label>
              <input
                type="text"
                value={bookingId}
                onChange={e => setBookingId(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Link to a booking"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium mb-1">
                Provider ID (optional)
              </label>
              <input
                type="text"
                value={providerId}
                onChange={e => setProviderId(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="If your issue is provider-specific"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium mb-1">
              Describe your issue
            </label>
            <textarea
              required
              value={message}
              onChange={e => setMessage(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 min-h-[100px]"
              placeholder="Give as much detail as possible so we can help you faster."
            />
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              disabled={creating}
            >
              {creating ? "Submitting…" : "Submit ticket"}
            </Button>
          </div>
        </form>
      </div>

      {/* Tickets list */}
      <div className="bg-white border rounded-lg shadow-sm p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold">My tickets</h2>
        </div>

        {loadingTickets && (
          <p className="text-sm text-gray-600">Loading tickets…</p>
        )}

        {ticketsError && (
          <div className="rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
            {ticketsError}
          </div>
        )}

        {!loadingTickets && !ticketsError && tickets.length === 0 && (
          <p className="text-sm text-gray-600">
            You don&apos;t have any support tickets yet.
          </p>
        )}

        {!loadingTickets && !ticketsError && tickets.length > 0 && (
          <div className="space-y-3">
            {tickets.map(t => (
              <button
                key={t.id}
                type="button"
                onClick={() =>
                  router.push(`/support/${encodeURIComponent(t.id)}`)
                }
                className="w-full text-left border rounded-md px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium truncate">{t.subject}</div>
                  <div className="text-xs text-gray-500 flex items-center gap-2">
                    <span className="px-2 py-[2px] rounded-full bg-gray-100 text-gray-700">
                      {t.status}
                    </span>
                    <span className="px-2 py-[2px] rounded-full bg-gray-100 text-gray-700">
                      {t.priority}
                    </span>
                  </div>
                </div>
                <div className="mt-1 text-xs text-gray-500 flex justify-between">
                  <span>Updated: {formatDateTime(t.last_activity_at)}</span>
                  {t.last_message && (
                    <span className="truncate max-w-[55%]">
                      Last: {t.last_message.body}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
