import { Loader2 } from "lucide-react";

export function LoadingSpinner({ className = "" }: { className?: string }) {
  return (
    <div className={`flex justify-center items-center ${className}`}>
      <Loader2 className="h-6 w-6 text-lime animate-spin" />
    </div>
  );
}
