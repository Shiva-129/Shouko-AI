"use client";

import { useRef, useEffect } from "react";
import { MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatPanelProps {
  artifactId: string;
  messages: Message[];
  isStreaming: boolean;
  sendMessage: (id: string, text: string) => Promise<void>;
}

export function ChatPanel({ artifactId, messages, isStreaming, sendMessage }: ChatPanelProps) {
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const input = inputRef.current;
    if (!input || !input.value.trim() || isStreaming) return;
    const text = input.value;
    input.value = "";
    await sendMessage(artifactId, text);
  };

  return (
    <Card className="bg-card border-border h-[calc(100vh-12rem)] flex flex-col">
      <div className="p-3 border-b border-border flex items-center gap-2">
        <MessageSquare className="h-4 w-4 text-lime" />
        <span className="text-xs font-mono text-secondaryText uppercase tracking-wider font-semibold">
          Chat
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 && (
          <p className="text-xs text-secondaryText/60 text-center mt-8 font-mono">
            Ask a question about this paper
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 text-xs leading-relaxed ${
                msg.role === "user"
                  ? "bg-lime text-[#0D0D0D] font-medium"
                  : "bg-slate-800/50 text-primaryText"
              }`}
            >
              {msg.content}
              {isStreaming && i === messages.length - 1 && msg.role === "assistant" && (
                <span className="animate-pulse">▊</span>
              )}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

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
    </Card>
  );
}
