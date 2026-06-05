"use client";

import { useRef, useEffect } from "react";
import { StreamingMessage } from "./StreamingMessage";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
}

export function MessageList({ messages, isStreaming }: MessageListProps) {
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
      {messages.length === 0 && (
        <p className="text-xs text-secondaryText/60 text-center mt-8 font-mono">
          Ask a question about this paper
        </p>
      )}
      {messages.map((msg, i) => {
        const isLast = i === messages.length - 1;
        const isAssistantStreaming = isStreaming && isLast && msg.role === "assistant";
        
        return (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 text-xs leading-relaxed ${
                msg.role === "user"
                  ? "bg-lime text-[#0D0D0D] font-medium"
                  : "bg-slate-800/50 text-primaryText"
              }`}
            >
              {msg.content}
              {isAssistantStreaming && <StreamingMessage />}
            </div>
          </div>
        );
      })}
      <div ref={chatEndRef} />
    </div>
  );
}
