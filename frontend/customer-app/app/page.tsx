"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

type TravelMode = "ANY" | "BUS" | "RAIL" | "FERRY" | "TAXI" | "SHUTTLE" | "OTHER";

export default function HomePage() {
  const router = useRouter();

  const today = new Date();
  const todayIso = today.toISOString().slice(0, 10); // YYYY-MM-DD

  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departureDate, setDepartureDate] = useState(todayIso);
  const [departureTime, setDepartureTime] = useState("ANY");
  const [passengers, setPassengers] = useState<number>(1);
  const [mode, setMode] = useState<TravelMode>("ANY");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!origin.trim() || !destination.trim()) {
      setError("Origin and destination are required.");
      return;
    }
    setError(null);

    const params = new URLSearchParams();
    params.set("origin", origin.trim());
    params.set("destination", destination.trim());
    params.set("date", departureDate);
    params.set("time", departureTime);
    params.set("pax", String(passengers));
    params.set("mode", mode);

    router.push(`/search?${params.toString()}`);
  }

  return (
    <div className="mt-10 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Find your next trip</h1>
        <p className="text-sm text-gray-600 mt-1">
          One customer app, connected to multiple transport providers. Search,
          compare, book, and travel.
        </p>
      </div>

      <div className="bg-white border rounded-lg shadow-sm p-4">
        {error && (
          <div className="mb-3 rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}

        <form
          onSubmit={handleSubmit}
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
            <Button type="submit" variant="primary">
              Search trips
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
