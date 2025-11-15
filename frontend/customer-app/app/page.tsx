"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  const router = useRouter();

  const [originLat, setOriginLat] = useState("");
  const [originLng, setOriginLng] = useState("");
  const [destLat, setDestLat] = useState("");
  const [destLng, setDestLng] = useState("");
  const [departureDate, setDepartureDate] = useState("");
  const [departureTime, setDepartureTime] = useState("");
  const [mode, setMode] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const dt = new Date(`${departureDate}T${departureTime || "00:00"}`);
    const iso = dt.toISOString();

    const params = new URLSearchParams({
      origin_lat: originLat,
      origin_lng: originLng,
      dest_lat: destLat,
      dest_lng: destLng,
      departure_time: iso
    });

    if (mode) {
      params.set("mode", mode);
    }

    router.push(`/search?${params.toString()}`);
  }

  return (
    <div className="max-w-2xl mx-auto mt-10 bg-white rounded-lg shadow-sm p-6">
      <h1 className="text-2xl font-semibold mb-2">
        Find your next trip with Geo-Connect
      </h1>
      <p className="text-sm text-gray-600 mb-6">
        Enter your origin, destination and departure time to see available
        services.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Origin latitude
            </label>
            <input
              type="number"
              required
              step="0.000001"
              value={originLat}
              onChange={e => setOriginLat(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="e.g. 6.5244"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Origin longitude
            </label>
            <input
              type="number"
              required
              step="0.000001"
              value={originLng}
              onChange={e => setOriginLng(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="e.g. 3.3792"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Destination latitude
            </label>
            <input
              type="number"
              required
              step="0.000001"
              value={destLat}
              onChange={e => setDestLat(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="e.g. 6.4654"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Destination longitude
            </label>
            <input
              type="number"
              required
              step="0.000001"
              value={destLng}
              onChange={e => setDestLng(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="e.g. 3.4064"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Departure date
            </label>
            <input
              type="date"
              required
              value={departureDate}
              onChange={e => setDepartureDate(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Departure time
            </label>
            <input
              type="time"
              required
              value={departureTime}
              onChange={e => setDepartureTime(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            Mode (optional)
          </label>
          <select
            value={mode}
            onChange={e => setMode(e.target.value)}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Any</option>
            <option value="BUS">Bus</option>
            <option value="TRAIN">Train</option>
            <option value="FERRY">Ferry</option>
            <option value="TAXI">Taxi</option>
          </select>
        </div>

        <Button type="submit" variant="primary" className="mt-2">
          Search trips
        </Button>
      </form>
    </div>
  );
}
