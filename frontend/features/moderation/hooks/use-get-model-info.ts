import { useQuery } from "@tanstack/react-query";

import { getModelInfo } from "@/lib/api-client";
import { QUERY_KEYS } from "@/constants/query-keys";

export const useGetModelInfo = () => {
  return useQuery({
    queryKey: QUERY_KEYS.MODEL_INFO,
    queryFn: getModelInfo,
  });
};
