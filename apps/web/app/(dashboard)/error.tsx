"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard error caught by boundary:", error);
  }, [error]);

  return (
    <div className="flex h-[80vh] flex-col items-center justify-center p-8 text-center">
      <div className="h-12 w-12 rounded-2xl bg-red-500/10 flex items-center justify-center border border-red-500/20 mb-4">
        <AlertTriangle className="h-6 w-6 text-red-500" />
      </div>
      <h2 className="font-syne font-bold text-lg text-primaryText mb-2">
        Something went wrong in the dashboard
      </h2>
      <p className="text-xs text-secondaryText font-mono max-w-md mb-6 leading-relaxed">
        {error.message || "An error occurred loading this page."}
      </p>
      <Button
        onClick={() => reset()}
        className="bg-lime text-[#0D0D0D] hover:bg-lime/90 font-bold text-xs px-6 py-2 rounded-lg"
      >
        Try Again
      </Button>
    </div>
  );
}
