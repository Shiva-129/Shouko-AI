"use client";

import { useRef } from "react";
import { Button } from "@/components/ui/button";

interface MessageInputProps {
  isStreaming: boolean;
  onSend: (text: string) => void;
}

export function MessageInput({ isStreaming, onSend }: MessageInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    const input = inputRef.current;
    if (!input || !input.value.trim() || isStreaming) return;
    onSend(input.value);
    input.value = "";
  };

  return (
    <div className="p-3 border-t border-border">
      <div className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          placeholder="Ask about this paper..."
          disabled={isStreaming}
          className="flex-1 bg-slate-800/50 border border-border rounded-lg px-3 py-2 text-xs text-primaryText placeholder:text-secondaryText/50 outline-none focus:border-lime/50 transition-colors disabled:opacity-50"
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSend();
          }}
        />
        <Button
          size="sm"
          className="bg-lime text-[#0D0D0D] hover:bg-lime/90 font-bold text-xs"
          disabled={isStreaming}
          onClick={handleSend}
        >
          Send
        </Button>
      </div>
    </div>
  );
}
