"use client";

import { MessageSquare } from "lucide-react";
import { Card } from "@/components/ui/card";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";

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
  const handleSend = async (text: string) => {
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

      <MessageList messages={messages} isStreaming={isStreaming} />

      <MessageInput isStreaming={isStreaming} onSend={handleSend} />
    </Card>
  );
}
