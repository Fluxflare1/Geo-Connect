"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { getCurrentUser } from "./auth";
import type { User } from "./types";

interface UseRequireAuthResult {
  user: User | null;
  checking: boolean;
}

export function useRequireAuth(): UseRequireAuthResult {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const u = getCurrentUser();
    if (!u) {
      const currentQuery = searchParams.toString();
      const fullPath = currentQuery ? `${pathname}?${currentQuery}` : pathname;
      const redirect = encodeURIComponent(fullPath);
      router.replace(`/login?redirect=${redirect}`);
      return;
    }

    setUser(u);
    setChecking(false);
  }, [router, pathname, searchParams]);

  return { user, checking };
}
