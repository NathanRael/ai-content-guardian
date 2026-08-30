import { useQuery } from "@tanstack/react-query";

import { getMetrics } from "@/lib/api-client";
import { QUERY_KEYS } from "@/constants/query-keys";

export const useGetMetrics = () => {
  return useQuery({
    queryKey: QUERY_KEYS.METRICS,
    queryFn: getMetrics,
  });
};
