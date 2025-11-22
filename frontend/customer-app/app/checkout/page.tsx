"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useRequireAuth } from "@/lib/use-require-auth";
import { apiFetch } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";

type PaymentMethod =
  | "CARD"
  | "WALLET"
  | "CASH"
  | "BANK_TRANSFER"
  | "AGENT";

interface TripSummaryProvider {
  id: string;
  name: string;
  logo_url: string;
}

interface TripSummaryStop {
  stop_id: string;
  name: string;
  city_code: string;
}

interface TripSummary {
  trip_id: string;
  provider: TripSummaryProvider;
  mode: string;
  product_type: string;
  origin: TripSummaryStop;
  destination: TripSummaryStop;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  available_seats: number;
  currency: string;
  total_price: string | number;
  per_passenger_price: string | number;
  fare_rules: Record<string, unknown>;
}

interface BookingCreateResponse {
  id: string;
  reference: string;
  status: string;
  payment_reference?: string | null;
}

function formatDateTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function CheckoutPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { checking } = useRequireAuth();

  const tripId = searchParams.get("trip_id");

  const [loadingTrip, setLoadingTrip] = useState(true);
  const [tripError, setTripError] = useState<string | null>(null);
  const [trip, setTrip] = useState<TripSummary | null>(null);

  const [passengerCount, setPassengerCount] = useState<number>(1);
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("CARD");

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (!tripId) {
      setTripError("Missing trip_id query parameter.");
      setLoadingTrip(false);
      return;
    }

    async function loadSummary() {
      setLoadingTrip(true);
      setTripError(null);
      try {
        const data = await apiFetch<TripSummary>(`/trips/${encodeURIComponent(tripId)}/summary`, {
          method: "GET"
        });
        setTrip(data);
        setPassengerCount(1);
      } catch (err: any) {
        setTripError(err.message || "Failed to load trip summary.");
      } finally {
        setLoadingTrip(false);
      }
    }

    void loadSummary();
  }, [tripId]);

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600 flex items-center gap-2">
        <Spinner size="sm" />
        <span>Checking your session…</span>
      </div>
    );
  }

  async function handleConfirmBooking(e: React.FormEvent) {
    e.preventDefault();
    if (!trip) return;

    if (!contactName.trim() || !contactEmail.trim() || !contactPhone.trim()) {
      setSubmitError("Please fill in contact name, email and phone.");
      return;
    }

    if (passengerCount < 1) {
      setSubmitError("Passenger count must be at least 1.");
      return;
    }
    if (passengerCount > trip.available_seats) {
      setSubmitError("Passenger count cannot exceed available seats.");
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      const payload = {
        trip_id: trip.trip_id,
        passengers: passengerCount,
        contact: {
          name: contactName.trim(),
          email: contactEmail.trim(),
          phone: contactPhone.trim()
        },
        payment_method: paymentMethod
      };

      const booking = await apiFetch<BookingCreateResponse>("/bookings", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      // If backend returns a payment_reference, send user to payment page.
      if (booking.payment_reference) {
        router.push(`/payment/${encodeURIComponent(booking.payment_reference)}`);
      } else {
        // Otherwise go straight to booking details.
        router.push(`/bookings/${encodeURIComponent(booking.id)}`);
      }
    } catch (err: any) {
      setSubmitError(err.message || "Failed to create booking.");
    } finally {
      setSubmitting(false);
    }
  }

  const totalPriceNumber =
    trip && typeof trip.total_price === "string"
      ? Number(trip.total_price)
      : trip?.total_price ?? 0;

  const perPassengerNumber =
    trip && typeof trip.per_passenger_price === "string"
      ? Number(trip.per_passenger_price)
      : trip?.per_passenger_price ?? 0;

  const effectiveTotal =
    perPassengerNumber && passengerCount
      ? perPassengerNumber * passengerCount
      : totalPriceNumber;

  return (
    <div className="mt-6 max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Checkout</h1>

      {tripError && (
        <div className="mb-4">
          <Alert variant="error" title="Could not load trip">
            {tripError}
          </Alert>
        </div>
      )}

      {loadingTrip && (
        <div className="mb-4 text-sm text-gray-600 flex items-center gap-2">
          <Spinner size="sm" />
          <span>Loading trip details…</span>
        </div>
      )}

      {trip && !loadingTrip && (
        <div className="grid gap-4 md:grid-cols-3">
          {/* Trip summary */}
          <div className="md:col-span-2 bg-white border rounded-lg shadow-sm p-4">
            <h2 className="text-sm font-semibold mb-2">Trip details</h2>
            <div className="text-sm">
              <div className="flex items-center gap-2 mb-1">
                <div className="font-semibold">
                  {trip.origin.name} → {trip.destination.name}
                </div>
                <span className="text-[11px] text-gray-500 uppercase">
                  {trip.mode}
                </span>
                {trip.product_type && (
                  <span className="text-[11px] text-gray-500">
                    • {trip.product_type}
                  </span>
                )}
              </div>
              <div className="text-xs text-gray-500 mb-1">
                Provider: {trip.provider.name}
              </div>
              <div className="text-xs text-gray-500 mb-1">
                Departure: {formatDateTime(trip.departure_time)}
              </div>
              <div className="text-xs text-gray-500 mb-1">
                Arrival: {formatDateTime(trip.arrival_time)}
              </div>
              <div className="text-xs text-gray-500 mb-1">
                Duration: {trip.duration_minutes} minutes
              </div>
              <div className="text-xs text-gray-500">
                Seats available: {trip.available_seats}
              </div>
            </div>
          </div>

          {/* Price + payment + contact form */}
          <div className="bg-white border rounded-lg shadow-sm p-4">
            <h2 className="text-sm font-semibold mb-2">Passenger & payment</h2>

            {submitError && (
              <div className="mb-2">
                <Alert variant="error" title="Could not create booking">
                  {submitError}
                </Alert>
              </div>
            )}

            <form onSubmit={handleConfirmBooking} className="space-y-3">
              <div>
                <label className="block text-xs font-medium mb-1">
                  Passengers
                </label>
                <input
                  type="number"
                  min={1}
                  max={trip.available_seats || 1}
                  value={passengerCount}
                  onChange={e =>
                    setPassengerCount(
                      Math.max(1, Math.min(trip.available_seats, Number(e.target.value) || 1))
                    )
                  }
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <p className="mt-1 text-[11px] text-gray-500">
                  Max {trip.available_seats} passengers for this trip.
                </p>
              </div>

              <div>
                <label className="block text-xs font-medium mb-1">
                  Contact name
                </label>
                <input
                  type="text"
                  value={contactName}
                  onChange={e => setContactName(e.target.value)}
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="Your full name"
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1">
                  Contact email
                </label>
                <input
                  type="email"
                  value={contactEmail}
                  onChange={e => setContactEmail(e.target.value)}
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1">
                  Contact phone
                </label>
                <input
                  type="tel"
                  value={contactPhone}
                  onChange={e => setContactPhone(e.target.value)}
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="+234..."
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1">
                  Payment method
                </label>
                <select
                  value={paymentMethod}
                  onChange={e =>
                    setPaymentMethod(e.target.value as PaymentMethod)
                  }
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm bg-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="CARD">Card (online)</option>
                  <option value="WALLET">Wallet</option>
                  <option value="CASH">Cash to driver / counter</option>
                  <option value="BANK_TRANSFER">Bank transfer</option>
                  <option value="AGENT">Pay through agent</option>
                </select>
              </div>

              <div className="border-t pt-2 mt-2 text-sm">
                <div className="flex justify-between text-xs text-gray-600">
                  <span>Per passenger</span>
                  <span>
                    {trip.currency}{" "}
                    {perPassengerNumber
                      ? perPassengerNumber.toLocaleString()
                      : "-"}
                  </span>
                </div>
                <div className="flex justify-between text-sm font-semibold mt-1">
                  <span>Total</span>
                  <span>
                    {trip.currency}{" "}
                    {effectiveTotal ? effectiveTotal.toLocaleString() : "-"}
                  </span>
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                disabled={submitting}
                className="w-full flex items-center justify-center gap-2 mt-2"
              >
                {submitting && <Spinner size="sm" />}
                <span>
                  {submitting ? "Confirming booking…" : "Confirm & continue"}
                </span>
              </Button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
