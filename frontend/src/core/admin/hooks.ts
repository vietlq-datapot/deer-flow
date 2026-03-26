import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { type AdminConfigUpdate, fetchAdminConfig, saveAdminConfig } from "./api";

export function useAdminConfig() {
  return useQuery({
    queryKey: ["admin-config"],
    queryFn: fetchAdminConfig,
    refetchOnWindowFocus: false,
  });
}

export function useSaveAdminConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (update: AdminConfigUpdate) => saveAdminConfig(update),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-config"] });
    },
  });
}
