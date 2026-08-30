"use client";

import * as React from "react";
import { Input } from "./input";
import { cn } from "@/lib/utils";

interface TimePickerProps {
  value?: string; // HH:mm format
  onChange: (value: string) => void;
  className?: string;
}

export const TimePicker = React.forwardRef<HTMLInputElement, TimePickerProps>(
  ({ value, onChange, className, ...props }, ref) => {
    return (
      <Input
        ref={ref}
        type="time"
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        className={cn("w-full", className)}
        {...props}
      />
    );
  }
);

TimePicker.displayName = "TimePicker";

