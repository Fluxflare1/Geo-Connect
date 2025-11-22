"use client";

import clsx from "clsx";

interface SpinnerProps {
  size?: "sm" | "md";
  className?: string;
}

export function Spinner({ size = "md", className }: SpinnerProps) {
  const dimension = size === "sm" ? "h-4 w-4" : "h-6 w-6";
  return (
    <div
      className={clsx(
        "inline-block animate-spin rounded-full border-2 border-current border-t-transparent align-middle",
        dimension,
        className
      )}
      aria-label="Loading"
    />
  );
}
