import { WebSocketConnectionStatus, WebSocketMessage } from './types';

export class SimulationWebSocketClient {
  private ws: WebSocket | null = null;
  private simulationId: string | null = null;
  private statusCallback: ((status: WebSocketConnectionStatus) => void) | null = null;
  private messageCallback: ((msg: WebSocketMessage) => void) | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private isIntentionallyClosed = false;

  constructor(
    private apiBaseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    private configuredWsBaseUrl: string | undefined = process.env.NEXT_PUBLIC_WS_URL
  ) {}

  public connect(
    simulationId: string,
    onMessage: (msg: WebSocketMessage) => void,
    onStatusChange: (status: WebSocketConnectionStatus) => void
  ) {
    this.disconnect();

    this.simulationId = simulationId;
    this.messageCallback = onMessage;
    this.statusCallback = onStatusChange;
    this.isIntentionallyClosed = false;

    this.initWebSocket();
  }

  private initWebSocket() {
    if (!this.simulationId) return;

    this.statusCallback?.('CONNECTING');

    // Prefer an explicit deployment WebSocket endpoint, otherwise derive it from REST.
    let wsBaseUrl = this.configuredWsBaseUrl
      ? this.configuredWsBaseUrl.replace(/\/$/, '')
      : `${this.apiBaseUrl.replace(/\/$/, '').replace(/^http/, 'ws')}/api/v1/simulations`;
    if (!wsBaseUrl.startsWith('ws://') && !wsBaseUrl.startsWith('wss://')) {
      wsBaseUrl = `ws://${wsBaseUrl}`;
    }

    const wsUrl = `${wsBaseUrl}/${this.simulationId}/ws`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.statusCallback?.('LIVE');
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data) as WebSocketMessage;
          this.messageCallback?.(parsed);
        } catch (err) {
          console.error('Failed to parse WS message JSON:', err);
        }
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket error:', err);
        this.statusCallback?.('ERROR');
      };

      this.ws.onclose = () => {
        if (!this.isIntentionallyClosed) {
          this.statusCallback?.('DISCONNECTED');
          this.scheduleReconnect();
        } else {
          this.statusCallback?.('DISCONNECTED');
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket instance:', err);
      this.statusCallback?.('ERROR');
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      if (!this.isIntentionallyClosed && this.simulationId) {
        this.initWebSocket();
      }
    }, 3000);
  }

  public disconnect() {
    this.isIntentionallyClosed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.statusCallback?.('DISCONNECTED');
  }
}
