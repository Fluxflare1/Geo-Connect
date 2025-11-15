"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api-client";
import type { TripSearchResult } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface TripSearchResponse {
  trips: TripSearchResult[];
  meta: {
    limit: number;
    offset: number;
    total: number | null;
  };
}

function formatTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: currency || "NGN"
  }).format(amount / 100); // assuming minor units
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [trips, setTrips] = useState<TripSearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTrips() {
      setLoading(true);
      setError(null);
      try {
        const qs = searchParams.toString();
        const data = await apiFetch<TripSearchResponse>(`/trips/search?${qs}`);
        setTrips(data.trips);
      } catch (err: any) {
        setError(err.message || "Failed to load trips.");
      } finally {
        setLoading(false);
      }
    }

    const required = [
      "origin_lat",
      "origin_lng",
      "dest_lat",
      "dest_lng",
      "departure_time"
    ];
    const missing = required.filter(key => !searchParams.get(key));
    if (missing.length > 0) {
      router.push("/");
      return;
    }

    loadTrips();
  }, [searchParams, router]);

  return (
    <div className="mt-6">
      <h1 className="text-xl font-semibold mb-3">Available trips</h1>

      {loading && <p className="text-sm text-gray-600">Searching for trips…</p>}

      {error && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 mb-4">
          {error}
        </div>
      )}

      {!loading && !error && trips.length === 0 && (
        <p className="text-sm text-gray-600">
          No trips found for your search. Try adjusting time or mode.
        </p>
      )}

      <div className="space-y-4">
        {trips.map(trip => {
          const seg = trip.segments[0];
          const fare = trip.fare_estimate;
          return (
            <div
              key={trip.id}
              className="bg-white rounded-lg shadow-sm border p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-gray-500 mb-1">
                  <span>{trip.provider_name}</span>
                  <span>•</span>
                  <span>{trip.mode}</span>
                  <span>•</span>
                  <span>{trip.total_distance_km} km</span>
                </div>
                <div className="flex items-center gap-4">
                  <div>
                    <div className="text-lg font-semibold">
                      {formatTime(seg.departure_time)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {seg.from_stop.name}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">→</div>
                  <div>
                    <div className="text-lg font-semibold">
                      {formatTime(seg.arrival_time)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {seg.to_stop.name}
                    </div>
                  </div>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Duration ~ {trip.duration_minutes} min • Seats available:{" "}
                  {trip.availability.seats_available}/{trip.availability.seats_total}
                </div>
                {seg.real_time_status && (
                  <div className="mt-1 text-xs text-gray-500">
                    Status: {seg.real_time_status.status}
                    {seg.real_time_status.delay_minutes > 0
                      ? ` (+${seg.real_time_status.delay_minutes} min)`
                      : ""}
                  </div>
                )}
              </div>

              <div className="flex flex-col items-start md:items-end gap-2">
                <div className="text-right">
                  <div className="text-base font-semibold">
                    {formatCurrency(fare.amount, fare.currency)}
                  </div>
                  <div className="text-xs text-gray-500">per passenger</div>
                </div>
                <Button
                  variant="primary"
                  onClick={() => {
                    const qs = searchParams.toString();
                    const base = `/checkout?tripId=${encodeURIComponent(trip.id)}`;
                    const url = qs ? `${base}&${qs}` : base;
                    router.push(url);
                  }}
                >
                  Select trip
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
