import { useState, useCallback } from "react";
import type { Message } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { createClient } = await import("@/lib/supabase");
  const supabase = createClient();
  if (supabase) {
    const { data } = await supabase.auth.getSession();
    if (data.session?.access_token) {
      return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${data.session.access_token}`,
      };
    }
  }
  return { "Content-Type": "application/json" };
}

export function useSSEChat(initialMessages: Message[] = []) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = useCallback(async (artifactId: string, userText: string) => {
    if (!userText.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: userText }]);
    setIsStreaming(true);
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${API_BASE}/conversations/${artifactId}/chat`, {
        method: "POST",
        headers,
        body: JSON.stringify({ message: userText }),
      });
      if (!response.ok || !response.body) {
        throw new Error("Failed to initialize stream from server.");
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let streamEnded = false;
      while (!streamEnded) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          if (trimmed.startsWith("data: ")) {
            const dataStr = trimmed.slice(6).trim();
            if (dataStr === "[DONE]") {
              streamEnded = true;
              break;
            }
            try {
              const data = JSON.parse(dataStr);
              if (data.token) {
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.role === "assistant") {
                    updated[updated.length - 1] = { ...last, content: last.content + data.token };
                  }
                  return updated;
                });
              } else if (data.error) {
                throw new Error(data.error);
              }
            } catch (err) {
              console.error("Error parsing stream token:", err);
            }
          }
        }
      }
    } catch (error) {
      console.warn("Backend SSE chat stream error:", error);
    } finally {
      setIsStreaming(false);
    }
  }, []);
  return { messages, setMessages, isStreaming, sendMessage };
}
