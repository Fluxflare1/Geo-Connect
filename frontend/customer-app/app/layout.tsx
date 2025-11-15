import "../styles/globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Geo-Connect – Customer",
  description: "Mobility-as-a-Service customer portal for Geo-Connect."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <header className="border-b bg-white">
          <div className="container flex items-center justify-between py-4">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-xl font-semibold">Geo-Connect</span>
            </Link>
            <nav className="flex items-center gap-4 text-sm">
              <Link href="/bookings">My bookings</Link>
              <Link href="/support">Support</Link>
              <Link href="/login">Login</Link>
            </nav>
          </div>
        </header>
        <main className="container py-6">{children}</main>
      </body>
    </html>
  );
}
