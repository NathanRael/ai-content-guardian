import { useQuery } from "@tanstack/react-query";

import { getBiasAudit } from "@/lib/api-client";
import { QUERY_KEYS } from "@/constants/query-keys";

export const useGetBiasAudit = () => {
  return useQuery({
    queryKey: QUERY_KEYS.BIAS_AUDIT,
    queryFn: getBiasAudit,
  });
};
