"use client";

import { useState } from "react";
import { AlertTriangle, X, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUpgradeModal } from "@/lib/hooks/useUpgradeModal";

interface UsageBannerProps {
  limitType: string;
}

export function UsageBanner({ limitType }: UsageBannerProps) {
  const [isDismissed, setIsDismissed] = useState(false);
  const upgradeModal = useUpgradeModal();

  if (isDismissed) return null;

  const handleUpgradeClick = () => {
    upgradeModal.open(
      "Upgrade to Pro",
      "Unlock unlimited summaries, deep-dive Q&A, and vector-search ingestions."
    );
  };

  return (
    <div className="mb-6 relative overflow-hidden rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4 text-primaryText transition-all">
      <div className="absolute top-0 right-0 w-32 h-32 bg-yellow-500/10 rounded-full blur-2xl pointer-events-none" />
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="h-8 w-8 rounded-lg bg-yellow-500/10 flex items-center justify-center border border-yellow-500/20 shrink-0 mt-0.5">
            <AlertTriangle className="h-4.5 w-4.5 text-yellow-500" />
          </div>
          <div>
            <h4 className="text-sm font-semibold font-syne text-primaryText">
              Nearing Limit: {limitType}
            </h4>
            <p className="text-xs text-secondaryText font-mono mt-1 max-w-2xl leading-relaxed">
              You&apos;ve consumed more than 80% of your current usage tier for {limitType}. Upgrade to the Pro plan to guarantee uninterrupted research capabilities and remove all daily/monthly limits.
            </p>
            <div className="flex items-center gap-3 mt-3">
              <Button
                onClick={handleUpgradeClick}
                size="sm"
                className="bg-yellow-500 text-black hover:bg-yellow-500/90 font-bold text-xs gap-1.5 h-8 px-3 rounded-lg"
              >
                <Sparkles className="h-3.5 w-3.5" />
                Upgrade to Pro
              </Button>
            </div>
          </div>
        </div>
        <button
          onClick={() => setIsDismissed(true)}
          className="text-secondaryText hover:text-primaryText transition-colors p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
