"use client";

import clsx from "clsx";
import { ReactNode } from "react";

type AlertVariant = "info" | "success" | "warning" | "error";

const baseClasses =
  "rounded-md px-3 py-2 text-sm flex items-start gap-2 border";

const variantClasses: Record<AlertVariant, string> = {
  info: "bg-blue-50 text-blue-800 border-blue-200",
  success: "bg-green-50 text-green-800 border-green-200",
  warning: "bg-yellow-50 text-yellow-800 border-yellow-200",
  error: "bg-red-50 text-red-800 border-red-200"
};

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children?: ReactNode;
  className?: string;
}

export function Alert({ variant = "info", title, children, className }: AlertProps) {
  const classes = clsx(baseClasses, variantClasses[variant], className);

  return (
    <div className={classes}>
      <div className="flex-1">
        {title && <div className="font-medium mb-0.5">{title}</div>}
        {children && <div className="text-xs sm:text-sm">{children}</div>}
      </div>
    </div>
  );
}
