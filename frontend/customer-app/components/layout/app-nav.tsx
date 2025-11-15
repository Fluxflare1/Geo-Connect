"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { getCurrentUser, logout } from "@/lib/auth";
import { useEffect, useState } from "react";

export default function AppNav() {
  const router = useRouter();
  const [hydrated, setHydrated] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    setHydrated(true);
    const user = getCurrentUser();
    setUserEmail(user?.email || null);
  }, []);

  function handleLogout() {
    logout();
    setUserEmail(null);
    router.push("/login");
  }

  return (
    <nav className="flex items-center gap-4 text-sm">
      <Link href="/bookings">My bookings</Link>
      <Link href="/support">Support</Link>

      {!hydrated ? null : userEmail ? (
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-600 truncate max-w-[140px]">
            {userEmail}
          </span>
          <button
            type="button"
            onClick={handleLogout}
            className="text-xs text-red-600 hover:underline"
          >
            Logout
          </button>
        </div>
      ) : (
        <Link href="/login">Login</Link>
      )}
    </nav>
  );
}
