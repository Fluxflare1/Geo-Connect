"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useRequireAuth } from "@/lib/use-require-auth";
import { apiFetch } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";

type TravelMode = "ANY" | "BUS" | "RAIL" | "FERRY" | "TAXI" | "SHUTTLE" | "OTHER";

interface TripSearchProvider {
  id: string;
  name: string;
  logo_url: string;
}

interface TripSearchStop {
  stop_id: string;
  name: string;
  city_code: string;
}

interface TripSearchPrice {
  currency: string;
  total: number;
  per_passenger: number;
  fees_included: boolean;
}

interface TripSearchResult {
  trip_id: string;
  provider: TripSearchProvider;
  mode: string;
  product_type: string;
  origin: TripSearchStop;
  destination: TripSearchStop;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  available_seats: number;
  price: TripSearchPrice;
  constraints: Record<string, boolean>;
  tags: string[];
  preview: Record<string, string>;
}

interface TripSearchResponse {
  search_id: string;
  currency: string;
  results: TripSearchResult[];
}

function formatDateTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { checking } = useRequireAuth();

  const today = new Date();
  const todayIso = today.toISOString().slice(0, 10); // YYYY-MM-DD

  const [origin, setOrigin] = useState(
    searchParams.get("origin") || ""
  ); // STOP_ID or city code
  const [destination, setDestination] = useState(
    searchParams.get("destination") || ""
  );
  const [departureDate, setDepartureDate] = useState(
    searchParams.get("date") || todayIso
  );
  const [departureTime, setDepartureTime] = useState(
    searchParams.get("time") || "ANY"
  );
  const [passengers, setPassengers] = useState<number>(
    Number(searchParams.get("pax") || 1)
  );
  const [mode, setMode] = useState<TravelMode>(
    (searchParams.get("mode") as TravelMode) || "ANY"
  );

  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [results, setResults] = useState<TripSearchResult[]>([]);
  const [searchId, setSearchId] = useState<string | null>(null);
  const [currency, setCurrency] = useState<string>("");

  // optional: auto-search if query params are present
  useEffect(() => {
    const autoOrigin = searchParams.get("origin");
    const autoDestination = searchParams.get("destination");
    const autoDate = searchParams.get("date");
    if (autoOrigin && autoDestination && autoDate) {
      handleSearch(false).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600 flex items-center gap-2">
        <Spinner size="sm" />
        <span>Checking your session…</span>
      </div>
    );
  }

  async function handleSearch(pushState: boolean = true) {
    if (!origin.trim() || !destination.trim()) {
      setSearchError("Origin and destination are required.");
      return;
    }

    setLoading(true);
    setSearchError(null);

    if (pushState) {
      const params = new URLSearchParams();
      params.set("origin", origin);
      params.set("destination", destination);
      params.set("date", departureDate);
      params.set("time", departureTime);
      params.set("pax", String(passengers));
      params.set("mode", mode);
      router.push(`/search?${params.toString()}`);
    }

    try {
      const body = {
        origin: {
          type: "STOP_ID", // you can later support CITY_CODE/COORDINATES in the UI
          value: origin.trim(),
        },
        destination: {
          type: "STOP_ID",
          value: destination.trim(),
        },
        departure_date: departureDate,
        departure_time: departureTime || "ANY",
        passengers,
        mode,
        filters: {
          providers: [],
          max_price: null,
          direct_only: false,
        },
        sort_by: "DEPARTURE_TIME",
        sort_order: "ASC",
      };

      const data = await apiFetch<TripSearchResponse>("/trips/search", {
        method: "POST",
        body: JSON.stringify(body),
      });

      setSearchId(data.search_id);
      setCurrency(data.currency);
      setResults(data.results || []);
    } catch (err: any) {
      setSearchError(err.message || "Failed to search trips.");
      setResults([]);
      setSearchId(null);
      setCurrency("");
    } finally {
      setLoading(false);
    }
  }

  function handleSelectTrip(tripId: string) {
    router.push(`/checkout?trip_id=${encodeURIComponent(tripId)}`);
  }

  return (
    <div className="mt-6 max-w-5xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Search trips</h1>

      {/* Search form */}
      <div className="bg-white border rounded-lg shadow-sm p-4 mb-4">
        {searchError && (
          <div className="mb-3">
            <Alert variant="error" title="Could not search trips">
              {searchError}
            </Alert>
          </div>
        )}

        <form
          onSubmit={e => {
            e.preventDefault();
            void handleSearch();
          }}
          className="grid gap-4 md:grid-cols-4 md:items-end"
        >
          <div className="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium mb-1">
                Origin (STOP ID)
              </label>
              <input
                type="text"
                value={origin}
                onChange={e => setOrigin(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="e.g. lagos-jibowu-terminal"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">
                Destination (STOP ID)
              </label>
              <input
                type="text"
                value={destination}
                onChange={e => setDestination(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="e.g. abuja-utako-terminal"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium mb-1">
                Departure date
              </label>
              <input
                type="date"
                value={departureDate}
                min={todayIso}
                onChange={e => setDepartureDate(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">
                Time of day
              </label>
              <select
                value={departureTime}
                onChange={e => setDepartureTime(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm bg-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="ANY">Any time</option>
                <option value="MORNING">Morning</option>
                <option value="AFTERNOON">Afternoon</option>
                <option value="EVENING">Evening</option>
                <option value="NIGHT">Night</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium mb-1">
                Passengers
              </label>
              <input
                type="number"
                min={1}
                max={10}
                value={passengers}
                onChange={e =>
                  setPassengers(Math.max(1, Number(e.target.value) || 1))
                }
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">
                Mode
              </label>
              <select
                value={mode}
                onChange={e => setMode(e.target.value as TravelMode)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm bg-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="ANY">Any</option>
                <option value="BUS">Bus / Coach</option>
                <option value="RAIL">Rail</option>
                <option value="FERRY">Ferry / Boat</option>
                <option value="TAXI">Taxi / Ride-hailing</option>
                <option value="SHUTTLE">Shuttle / Minibus</option>
              </select>
            </div>
          </div>

          <div className="md:col-span-4 flex justify-end">
            <Button
              type="submit"
              variant="primary"
              disabled={loading}
              className="flex items-center gap-2"
            >
              {loading && <Spinner size="sm" />}
              <span>{loading ? "Searching…" : "Search trips"}</span>
            </Button>
          </div>
        </form>
      </div>

      {/* Results */}
      <div className="bg-white border rounded-lg shadow-sm p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold">Results</h2>
          {searchId && (
            <span className="text-[11px] text-gray-500">
              Search ID: <span className="font-mono">{searchId}</span>
            </span>
          )}
        </div>

        {loading && (
          <p className="text-sm text-gray-600 flex items-center gap-2">
            <Spinner size="sm" />
            <span>Looking for available trips…</span>
          </p>
        )}

        {!loading && !searchError && results.length === 0 && (
          <p className="text-sm text-gray-600">
            No trips found for the selected criteria. Try changing your stops,
            date or time.
          </p>
        )}

        {!loading && results.length > 0 && (
          <div className="space-y-3">
            {results.map(result => (
              <div
                key={result.trip_id}
                className="border rounded-lg px-3 py-2 text-sm flex flex-col md:flex-row md:items-center md:justify-between gap-2"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <div className="font-semibold">
                      {result.origin.name} → {result.destination.name}
                    </div>
                    <span className="text-[11px] text-gray-500 uppercase">
                      {result.mode}
                    </span>
                    {result.product_type && (
                      <span className="text-[11px] text-gray-500">
                        • {result.product_type}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {result.provider.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    Depart: {formatDateTime(result.departure_time)} • Arrive:{" "}
                    {formatDateTime(result.arrival_time)} •{" "}
                    {result.duration_minutes} mins
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Seats left:{" "}
                    <span className="font-semibold">
                      {result.available_seats}
                    </span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div className="text-sm font-semibold">
                    {result.price.currency}{" "}
                    {result.price.total.toLocaleString()}
                  </div>
                  <Button
                    type="button"
                    size="sm"
                    variant="primary"
                    onClick={() => handleSelectTrip(result.trip_id)}
                  >
                    Select
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
