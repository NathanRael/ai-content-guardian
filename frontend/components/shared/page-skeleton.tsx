import React from "react";
import { Skeleton } from "../ui/skeleton";

const PageSkeleton = () => {
  return (
    <div className="app-section space-y-10 mx-auto pb-10">
      <div className="flex items-center justify-between w-full">
        <Skeleton className="h-20 w-[30%]" />
        <Skeleton className="h-10 w-[10%]" />
      </div>
      <Skeleton className="h-60 w-full" />
      <Skeleton className="h-10 ms-auto w-[20%]" />
    </div>
  );
};

export default PageSkeleton;
