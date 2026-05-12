"use client";

import { useEffect, useState } from "react";
import type { LiveMessage } from "@/types";

export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<LiveMessage[]>([]);

  useEffect(() => {
    const url = `${process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"}/ws/live`;
    const ws = new WebSocket(url);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data) as LiveMessage;
      setMessages((current) => [message, ...current].slice(0, 10));
    };
    return () => ws.close();
  }, []);

  return { connected, messages };
}
