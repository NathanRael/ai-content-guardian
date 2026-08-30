"use client";

import { X } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { useModerationStore } from "@/store/moderation-store";

export function ClearStorageButton() {
  const clearAll = useModerationStore((state) => state.clearAll);

  const handleClear = () => {
    clearAll();
    toast.success("Données de l’interface effacées.");
  };

  return (
    <Button
      variant="outline"
      size="icon"
      className="fixed bottom-6 right-6 z-50 rounded-full shadow-sm"
      onClick={handleClear}
      aria-label="Effacer toutes les données de l’interface"
      data-cy="clear-storage-button"
    >
      <X className="size-4" />
    </Button>
  );
}
