"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api";
import { Sparkles, Check, Loader2, Zap } from "lucide-react";

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
}

export function UpgradeModal({ 
  isOpen, 
  onClose, 
  title = "Usage Limit Reached", 
  description = "You have hit the monthly usage threshold for your Free account." 
}: UpgradeModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpgrade = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.post<{ url: string }>("/billing/checkout");
      if (res.url) {
        window.location.href = res.url;
      } else {
        throw new Error("Failed to retrieve checkout URL");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to initiate upgrade. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    "Unlimited automated PDF paper summaries",
    "Unlimited deep-dive insights and Q&A suggestions",
    "Unlimited semantic search paper ingestions",
    "Priority processing with zero queue times",
    "Centralized Collections & document organization",
  ];

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[440px] bg-[#0E1117] border-border text-primaryText">
        <div className="absolute top-0 right-0 w-48 h-48 bg-lime/10 rounded-full blur-3xl pointer-events-none" />
        
        <DialogHeader className="text-left space-y-2 relative">
          <div className="h-10 w-10 rounded-xl bg-lime/20 flex items-center justify-center border border-lime/30 mb-2">
            <Zap className="h-5 w-5 text-lime animate-pulse" />
          </div>
          <DialogTitle className="font-syne font-bold text-xl leading-tight">
            {title}
          </DialogTitle>
          <DialogDescription className="text-secondaryText text-xs font-mono">
            {description}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-3 relative">
          <h4 className="text-xs font-mono uppercase tracking-wider text-secondaryText/80 font-bold">
            What's included in Pro:
          </h4>
          
          <ul className="space-y-2.5">
            {features.map((f, i) => (
              <li key={i} className="flex items-start gap-2 text-xs">
                <Check className="h-4 w-4 text-lime shrink-0 mt-0.5" />
                <span className="text-primaryText/90 leading-tight">{f}</span>
              </li>
            ))}
          </ul>
        </div>

        {error && (
          <p className="text-xs text-red-400 font-mono mt-1">{error}</p>
        )}

        <div className="flex flex-col gap-2 mt-4 relative">
          <Button 
            onClick={handleUpgrade} 
            disabled={isLoading}
            className="w-full bg-lime text-[#0D0D0D] hover:bg-lime/90 font-bold text-sm py-5"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4 mr-2" />
            )}
            Upgrade to Pro — $15/month
          </Button>
          <Button 
            variant="ghost" 
            onClick={onClose}
            className="w-full text-secondaryText hover:text-primaryText text-xs font-mono"
          >
            Maybe later
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
