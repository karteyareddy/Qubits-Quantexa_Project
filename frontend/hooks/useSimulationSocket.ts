'use client';

import { useEffect, useRef, useState } from 'react';
import { SimulationWebSocketClient } from '../lib/websocket';
import { WebSocketConnectionStatus, WebSocketMessage } from '../lib/types';

export function useSimulationSocket(
  simulationId: string | null,
  onMessage?: (msg: WebSocketMessage) => void
) {
  const [status, setStatus] = useState<WebSocketConnectionStatus>('DISCONNECTED');
  const clientRef = useRef<SimulationWebSocketClient | null>(null);

  useEffect(() => {
    if (!simulationId) {
      if (clientRef.current) {
        clientRef.current.disconnect();
        clientRef.current = null;
      }
      return;
    }

    const client = new SimulationWebSocketClient();
    clientRef.current = client;

    client.connect(
      simulationId,
      (msg) => {
        onMessage?.(msg);
      },
      (newStatus) => {
        setStatus(newStatus);
      }
    );

    return () => {
      client.disconnect();
      clientRef.current = null;
    };
  }, [simulationId, onMessage]);

  return { status };
}
