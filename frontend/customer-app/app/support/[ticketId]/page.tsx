"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import { useRequireAuth } from "@/lib/auth-context";
import type { SupportTicketDetail, SupportMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";

function formatDateTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function SupportTicketDetailPage() {
  const { checking } = useRequireAuth();

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600">
        Checking your session…
      </div>
    );
  }

  const params = useParams<{ ticketId: string }>();
  const router = useRouter();

  const ticketId = params.ticketId;

  const [ticket, setTicket] = useState<SupportTicketDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [messageBody, setMessageBody] = useState("");
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    async function loadTicket() {
      setLoading(true);
      setError(null);
      try {
        const data = await apiFetch<SupportTicketDetail>(
          `/support/tickets/${ticketId}`
        );
        setTicket(data);
      } catch (err: any) {
        setError(err.message || "Failed to load ticket.");
      } finally {
        setLoading(false);
      }
    }

    if (!ticketId) {
      router.push("/support");
      return;
    }

    if (!checking) {
      loadTicket();
    }
  }, [ticketId, router, checking]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [ticket]);

  async function handleSendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!ticket) return;
    if (!messageBody.trim()) return;

    setSending(true);
    setSendError(null);

    try {
      await apiFetch(`/support/tickets/${ticket.id}/messages`, {
        method: "POST",
        body: JSON.stringify({ body: messageBody.trim() })
      });

      setMessageBody("");

      // reload ticket to get latest messages
      const data = await apiFetch<SupportTicketDetail>(
        `/support/tickets/${ticket.id}`
      );
      setTicket(data);
    } catch (err: any) {
      setSendError(err.message || "Failed to send message.");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="mt-6 max-w-3xl mx-auto flex flex-col h-[calc(100vh-120px)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <button
            type="button"
            className="text-xs text-gray-500 hover:underline mb-1"
            onClick={() => router.push("/support")}
          >
            ← Back to tickets
          </button>
          <h1 className="text-lg font-semibold">
            {ticket ? ticket.subject : "Ticket"}
          </h1>
          {ticket && (
            <div className="text-xs text-gray-500">
              Status:{" "}
              <span className="font-semibold">{ticket.status}</span>{" "}
              • Priority:{" "}
              <span className="font-semibold">{ticket.priority}</span>{" "}
              • Created: {formatDateTime(ticket.created_at)}
            </div>
          )}
        </div>
      </div>

      {loading && (
        <p className="text-sm text-gray-600">Loading conversation…</p>
      )}

      {error && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 mb-4">
          {error}
        </div>
      )}

      {ticket && (
        <>
          {/* Messages */}
          <div className="flex-1 min-h-0 overflow-y-auto border rounded-lg bg-white p-3 mb-3">
            {ticket.messages.length === 0 && (
              <p className="text-xs text-gray-500">
                No messages yet. Start the conversation below.
              </p>
            )}

            <div className="space-y-3">
              {ticket.messages.map(m => (
                <MessageBubble key={m.id} message={m} />
              ))}
            </div>
            <div ref={messagesEndRef} />
          </div>

          {/* Send box */}
          <form
            onSubmit={handleSendMessage}
            className="border rounded-lg bg-white p-3"
          >
            {sendError && (
              <div className="mb-2 rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
                {sendError}
              </div>
            )}

            <label className="block text-xs font-medium mb-1">
              Your message
            </label>
            <textarea
              value={messageBody}
              onChange={e => setMessageBody(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 min-h-[80px]"
              placeholder="Type your reply…"
            />
            <div className="mt-2 flex justify-end">
              <Button
                type="submit"
                variant="primary"
                disabled={sending || !messageBody.trim()}
              >
                {sending ? "Sending…" : "Send"}
              </Button>
            </div>
          </form>
        </>
      )}
    </div>
  );
}

function MessageBubble({ message }: { message: SupportMessage }) {
  const isCustomer = message.sender_type === "CUSTOMER";
  const alignClass = isCustomer ? "items-end" : "items-start";
  const bubbleClass = isCustomer
    ? "bg-blue-600 text-white"
    : "bg-gray-100 text-gray-900";

  const label = message.sender_name || message.sender_type;

  return (
    <div className={`flex flex-col ${alignClass}`}>
      <div className="text-[11px] text-gray-500 mb-[2px]">
        {label} • {new Date(message.created_at).toLocaleString()}
      </div>
      <div
        className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${bubbleClass}`}
      >
        {message.body}
      </div>
    </div>
  );
}
