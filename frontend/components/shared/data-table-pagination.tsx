import { Button } from "@/components/ui/button";
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";

interface DataTablePaginationProps {
  pageIndex: number;
  pageCount: number;
  onPageChange: (page: number) => void;
  disabled?: boolean;
}

export function DataTablePagination({
  pageIndex,
  pageCount,
  onPageChange,
  disabled = false,
}: DataTablePaginationProps) {
  const getPaginationItems = () => {
    if (pageCount <= 7) {
      return Array.from({ length: pageCount }, (_, i) => i + 1);
    }

    const pages: (number | string)[] = [];

    pages.push(1, 2);

    if (pageIndex > 4) {
      pages.push("...");
    }

    const startWindow = Math.max(3, pageIndex - 1);
    const endWindow = Math.min(pageCount - 2, pageIndex + 1);

    for (let i = startWindow; i <= endWindow; i++) {
      if (i > 2 && i < pageCount - 1) {
        pages.push(i);
      }
    }

    if (pageIndex < pageCount - 3) {
      pages.push("...");
    }

    pages.push(pageCount - 1, pageCount);

    return Array.from(new Set(pages));
  };

  return (
    <div className="flex items-center justify-end px-2 w-full py-4">
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          className="h-8 w-8 p-0"
          onClick={() => onPageChange(1)}
          disabled={pageIndex <= 1 || disabled}
        >
          <span className="sr-only">Allez à la première page</span>
          <ChevronsLeft className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          className="h-8 w-8 p-0"
          onClick={() => onPageChange(pageIndex - 1)}
          disabled={pageIndex <= 1 || disabled}
        >
          <span className="sr-only">Aller à la page précédente</span>
          <ChevronLeft className="h-4 w-4" />
        </Button>

        {getPaginationItems().map((item, index) =>
          item === "..." ? (
            <span
              key={`ellipsis-${index}`}
              className="px-2 text-muted-foreground"
            >
              ...
            </span>
          ) : (
            <Button
              key={item}
              variant={pageIndex === item ? "accent" : "outline"}
              className="h-8 w-8 p-0"
              onClick={() => onPageChange(Number(item))}
              disabled={disabled}
            >
              {item}
            </Button>
          )
        )}

        <Button
          variant="outline"
          className="h-8 w-8 p-0"
          onClick={() => onPageChange(pageIndex + 1)}
          disabled={pageIndex >= pageCount || disabled}
        >
          <span className="sr-only">Aller à la page suivante</span>
          <ChevronRight className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          className="h-8 w-8 p-0"
          onClick={() => onPageChange(pageCount)}
          disabled={pageIndex >= pageCount || disabled}
        >
          <span className="sr-only">Aller à la dernière page</span>
          <ChevronsRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
