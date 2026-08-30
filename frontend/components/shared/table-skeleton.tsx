import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

const TableSkeleton = ({
  description = "Chargement des données...",
  className,
}: {
  description?: string;
  className?: string;
}) => {
  return (
    <div
      className={cn(
        `flex flex-col gap-2 items-center justify-center h-60 w-full p-6 rounded-lg border border-border`,
        className,
      )}
    >
      <Loader2 className="animate-spin size-10 text-primary" />
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
};

export default TableSkeleton;
