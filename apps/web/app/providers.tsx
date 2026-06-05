"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import posthog from "posthog-js";
import { UpgradeModal } from "@/components/shared/UpgradeModal";
import { useUpgradeModal } from "@/lib/hooks/useUpgradeModal";

export function Providers({ children }: { children: React.ReactNode }) {
  const upgradeModal = useUpgradeModal();
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000,
            retry: 2,
          },
        },
      })
  );

  useEffect(() => {
    const key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
    const host = process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://app.posthog.com";
    if (key) {
      posthog.init(key, {
        api_host: host,
        capture_pageview: true,
        loaded: (ph) => {
          if (process.env.NODE_ENV === "development") ph.opt_out_capturing();
        },
      });
    }
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <UpgradeModal
        isOpen={upgradeModal.isOpen}
        onClose={upgradeModal.close}
        title={upgradeModal.title}
        description={upgradeModal.description}
      />
    </QueryClientProvider>
  );
}
