"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { useRequireAuth } from "@/lib/use-require-auth";
import { apiFetch } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import type { User } from "@/lib/types";
import { getCurrentUser } from "@/lib/auth";

interface CheckoutTripSummary {
  trip_id: string;
  provider_name: string;
  origin_name: string;
  destination_name: string;
  departure_time: string;
  arrival_time: string;
  currency: string;
  total_price: number;
}

interface CreateBookingResponse {
  id: string;
  reference: string;
  status: string;
  payment_reference?: string;
}

export default function CheckoutPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, checking } = useRequireAuth();

  const [trip, setTrip] = useState<CheckoutTripSummary | null>(null);
  const [loadingTrip, setLoadingTrip] = useState(true);
  const [tripError, setTripError] = useState<string | null>(null);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [seats, setSeats] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (checking) return;

    const tripId = searchParams.get("trip_id");
    if (!tripId) {
      setTripError("Missing trip identifier. Please select a trip again.");
      setLoadingTrip(false);
      return;
    }

    const localUser: User | null = user ?? getCurrentUser();
    if (localUser) {
      const name = [localUser.first_name, localUser.last_name]
        .filter(Boolean)
        .join(" ");
      if (name) setFullName(name);
      if (localUser.email) setEmail(localUser.email);
      if (localUser.phone_number) setPhoneNumber(localUser.phone_number);
    }

    async function loadTrip() {
      setLoadingTrip(true);
      setTripError(null);
      try {
        const data = await apiFetch<CheckoutTripSummary>(
          `/trips/${encodeURIComponent(tripId)}/summary`
        );
        setTrip(data);
      } catch (err: any) {
        setTripError(
          err.message || "Failed to load trip details for checkout."
        );
      } finally {
        setLoadingTrip(false);
      }
    }

    loadTrip();
  }, [checking, searchParams, user]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!trip) return;

    if (!fullName.trim() || !email.trim() || !phoneNumber.trim()) {
      setSubmitError("Name, email and phone number are required.");
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      const [firstName, ...rest] = fullName.trim().split(" ");
      const lastName = rest.join(" ");

      const idempotencyKey = uuidv4();

      const payload = {
        trip_id: trip.trip_id,
        seats,
        passenger: {
          first_name: firstName,
          last_name: lastName || "",
          email,
          phone_number: phoneNumber
        }
      };

      const booking = await apiFetch<CreateBookingResponse>("/bookings", {
        method: "POST",
        headers: {
          "Idempotency-Key": idempotencyKey
        },
        body: JSON.stringify(payload)
      });

      if (booking.payment_reference) {
        router.push(`/payment/${encodeURIComponent(booking.payment_reference)}`);
      } else {
        router.push(`/bookings/${encodeURIComponent(booking.id)}`);
      }
    } catch (err: any) {
      setSubmitError(err.message || "Failed to create booking.");
    } finally {
      setSubmitting(false);
    }
  }

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600 flex items-center gap-2">
        <Spinner size="sm" />
        <span>Checking your session…</span>
      </div>
    );
  }

  return (
    <div className="mt-6 max-w-4xl mx-auto grid gap-6 md:grid-cols-[2fr,1.2fr]">
      <div className="bg-white border rounded-lg shadow-sm p-4">
        <h1 className="text-xl font-semibold mb-4">Passenger details</h1>

        {submitError && (
          <div className="mb-3">
            <Alert variant="error" title="Could not create booking">
              {submitError}
            </Alert>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium mb-1">
              Full name
            </label>
            <input
              type="text"
              value={fullName}
              onChange={e => setFullName(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="e.g. Jane Doe"
              required
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium mb-1">
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">
                Phone number
              </label>
              <input
                type="tel"
                value={phoneNumber}
                onChange={e => setPhoneNumber(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium mb-1">
              Number of seats
            </label>
            <input
              type="number"
              min={1}
              max={10}
              value={seats}
              onChange={e => setSeats(Number(e.target.value) || 1)}
              className="block w-32 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              disabled={submitting || !trip}
              className="flex items-center gap-2"
            >
              {submitting && <Spinner size="sm" />}
              <span>{submitting ? "Processing…" : "Continue to payment"}</span>
            </Button>
          </div>
        </form>
      </div>

      <div className="bg-white border rounded-lg shadow-sm p-4">
        <h2 className="text-sm font-semibold mb-3">Trip summary</h2>

        {loadingTrip && (
          <p className="text-xs text-gray-600 flex items-center gap-2">
            <Spinner size="sm" />
            <span>Loading trip details…</span>
          </p>
        )}

        {tripError && (
          <Alert variant="error" title="Could not load trip">
            {tripError}
          </Alert>
        )}

        {trip && !tripError && (
          <div className="space-y-3 text-sm">
            <div>
              <div className="text-xs text-gray-500">Provider</div>
              <div className="font-medium">{trip.provider_name}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Route</div>
              <div className="font-medium">
                {trip.origin_name} → {trip.destination_name}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-gray-500">Departure</div>
                <div className="font-medium">
                  {new Date(trip.departure_time).toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Arrival (est.)</div>
                <div className="font-medium">
                  {new Date(trip.arrival_time).toLocaleString()}
                </div>
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Total price</div>
              <div className="font-semibold">
                {trip.currency} {trip.total_price.toFixed(2)}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
