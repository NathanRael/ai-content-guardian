"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

import { cn } from "@/lib/utils";

interface CollapsibleSectionProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export function CollapsibleSection({
  title,
  children,
  className,
}: CollapsibleSectionProps) {
  const [open, setOpen] = useState(false);

  return (
    <div
      className={cn(
        "rounded-lg border border-background-200 bg-background",
        className,
      )}
    >
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center justify-between gap-3 p-4 text-left font-medium"
      >
        {title}
        <ChevronDown
          className={cn(
            "size-4 shrink-0 text-muted-foreground transition-transform",
            open && "rotate-180",
          )}
        />
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}
