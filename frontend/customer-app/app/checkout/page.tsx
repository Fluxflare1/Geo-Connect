"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import { useRequireAuth } from "@/lib/auth-context";
import type {
  TripSearchResult,
  BookingCreateResponse
} from "@/lib/types";
import { Button } from "@/components/ui/button";

interface TripSearchResponse {
  trips: TripSearchResult[];
  meta: {
    limit: number;
    offset: number;
    total: number | null;
  };
}

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: currency || "NGN"
  }).format(amount / 100);
}

function generateIdempotencyKey() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `gc_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

interface PassengerForm {
  type: "ADULT" | "CHILD" | "SENIOR";
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
}

export default function CheckoutPage() {
  const { checking } = useRequireAuth();

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600">
        Checking your session…
      </div>
    );
  }

  const searchParams = useSearchParams();
  const router = useRouter();

  const tripId = searchParams.get("tripId");

  const [loadingTrip, setLoadingTrip] = useState(true);
  const [trip, setTrip] = useState<TripSearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [passengers, setPassengers] = useState<PassengerForm[]>([
    {
      type: "ADULT",
      first_name: "",
      last_name: "",
      email: "",
      phone: ""
    }
  ]);

  const [paymentProvider, setPaymentProvider] = useState("paystack");
  const [currency, setCurrency] = useState("NGN");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tripId) {
      router.push("/");
      return;
    }

    async function loadTrip() {
      setLoadingTrip(true);
      setError(null);
      try {
        const qs = searchParams.toString();
        const data = await apiFetch<TripSearchResponse>(`/trips/search?${qs}`);
        const found = data.trips.find(t => t.id === tripId);
        if (!found) {
          setError("Selected trip not found. Please search again.");
        } else {
          setTrip(found);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load trip details.");
      } finally {
        setLoadingTrip(false);
      }
    }

    if (!checking) {
      loadTrip();
    }
  }, [tripId, searchParams, router, checking]);

  function updatePassenger(
    index: number,
    field: keyof PassengerForm,
    value: string
  ) {
    setPassengers(prev => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  }

  function addPassenger() {
    setPassengers(prev => [
      ...prev,
      { type: "ADULT", first_name: "", last_name: "", email: "", phone: "" }
    ]);
  }

  function removePassenger(index: number) {
    setPassengers(prev => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!trip) return;

    setSubmitting(true);
    setError(null);

    try {
      const payload = {
        trip_id: trip.id,
        passengers: passengers.map(p => ({
          type: p.type,
          first_name: p.first_name,
          last_name: p.last_name,
          email: p.email,
          phone: p.phone
        })),
        seat_selection: {
          enabled: false,
          requested_seats: [] as string[]
        },
        payment: {
          provider: paymentProvider,
          currency,
          amount: 0 // backend recomputes from pricing; we intentionally ignore client amount
        }
      };

      const idempotencyKey = generateIdempotencyKey();

      const response = await apiFetch<BookingCreateResponse>("/bookings", {
        method: "POST",
        headers: {
          "Idempotency-Key": idempotencyKey
        },
        body: JSON.stringify(payload)
      });

      // persist payment session locally for payment page
      if (typeof window !== "undefined") {
        window.localStorage.setItem(
          "gc_last_payment_session",
          JSON.stringify(response.payment_session)
        );
      }

      const bookingId = response.booking.id;
      const ref = response.payment_session.payment_reference;

      router.push(
        `/payment/${encodeURIComponent(
          ref
        )}?bookingId=${encodeURIComponent(bookingId)}`
      );
    } catch (err: any) {
      setError(err.message || "Failed to create booking.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mt-6 max-w-3xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Trip checkout</h1>

      {loadingTrip && (
        <p className="text-sm text-gray-600">Loading trip details…</p>
      )}

      {error && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 mb-4">
          {error}
        </div>
      )}

      {trip && (
        <>
          {/* Trip summary */}
          <div className="mb-6 bg-white border rounded-lg shadow-sm p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs uppercase tracking-wide text-gray-500 mb-1">
                  {trip.provider_name} • {trip.mode} •{" "}
                  {trip.total_distance_km} km
                </div>
                <div className="text-sm text-gray-600">
                  Seats available: {trip.availability.seats_available}/
                  {trip.availability.seats_total}
                </div>
              </div>
              <div className="text-right">
                <div className="text-base font-semibold">
                  {formatCurrency(
                    trip.fare_estimate.amount,
                    trip.fare_estimate.currency
                  )}
                </div>
                <div className="text-xs text-gray-500">per passenger</div>
              </div>
            </div>
          </div>

          {/* Booking form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="bg-white border rounded-lg shadow-sm p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold">Passengers</h2>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={addPassenger}
                >
                  Add passenger
                </Button>
              </div>

              <div className="space-y-4">
                {passengers.map((p, index) => (
                  <div
                    key={index}
                    className="border rounded-md p-3 flex flex-col gap-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-gray-600">
                        Passenger {index + 1}
                      </span>
                      {passengers.length > 1 && (
                        <button
                          type="button"
                          className="text-xs text-red-600 hover:underline"
                          onClick={() => removePassenger(index)}
                        >
                          Remove
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-medium mb-1">
                          Type
                        </label>
                        <select
                          value={p.type}
                          onChange={e =>
                            updatePassenger(
                              index,
                              "type",
                              e.target.value as PassengerForm["type"]
                            )
                          }
                          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        >
                          <option value="ADULT">Adult</option>
                          <option value="CHILD">Child</option>
                          <option value="SENIOR">Senior</option>
                        </select>
                      </div>
                      <div />
                      <div>
                        <label className="block text-xs font-medium mb-1">
                          First name
                        </label>
                        <input
                          type="text"
                          required
                          value={p.first_name}
                          onChange={e =>
                            updatePassenger(index, "first_name", e.target.value)
                          }
                          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium mb-1">
                          Last name
                        </label>
                        <input
                          type="text"
                          required
                          value={p.last_name}
                          onChange={e =>
                            updatePassenger(index, "last_name", e.target.value)
                          }
                          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium mb-1">
                          Email
                        </label>
                        <input
                          type="email"
                          value={p.email}
                          onChange={e =>
                            updatePassenger(index, "email", e.target.value)
                          }
                          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                          placeholder="Optional"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium mb-1">
                          Phone
                        </label>
                        <input
                          type="tel"
                          value={p.phone}
                          onChange={e =>
                            updatePassenger(index, "phone", e.target.value)
                          }
                          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                          placeholder="Optional"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Payment */}
            <div className="bg-white border rounded-lg shadow-sm p-4">
              <h2 className="text-sm font-semibold mb-3">Payment</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium mb-1">
                    Payment provider
                  </label>
                  <select
                    value={paymentProvider}
                    onChange={e => setPaymentProvider(e.target.value)}
                    className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="paystack">Paystack</option>
                    <option value="flutterwave">Flutterwave</option>
                    <option value="stripe">Stripe</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1">
                    Currency
                  </label>
                  <select
                    value={currency}
                    onChange={e => setCurrency(e.target.value)}
                    className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="NGN">NGN</option>
                    <option value="USD">USD</option>
                  </select>
                </div>
              </div>

              {trip && (
                <div className="mt-4 text-sm text-gray-700">
                  Estimated total:{" "}
                  <span className="font-semibold">
                    {formatCurrency(
                      trip.fare_estimate.amount * passengers.length,
                      trip.fare_estimate.currency
                    )}
                  </span>{" "}
                  ({passengers.length}{" "}
                  {passengers.length === 1 ? "passenger" : "passengers"})
                </div>
              )}
            </div>

            <div className="flex justify-end">
              <Button
                type="submit"
                variant="primary"
                disabled={submitting || !trip}
              >
                {submitting ? "Creating booking…" : "Confirm & continue to payment"}
              </Button>
            </div>
          </form>
        </>
      )}
    </div>
  );
}
