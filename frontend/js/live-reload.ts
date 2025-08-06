/**
 * Live Reload Client
 * Connects to WebSocket server and automatically reloads the page when files change
 */

interface ReloadMessage {
    type: 'reload';
    file: string;
    timestamp: number;
}

class LiveReloadClient {
    private ws: WebSocket | null = null;
    private reconnectAttempts: number = 0;
    private readonly maxReconnectAttempts: number = 5;
    private reconnectDelay: number = 1000; // Start with 1 second
    private isConnected: boolean = false;
    private isReloading: boolean = false;

    constructor() {
        // Only enable in development
        if (this.isDevelopment()) {
            this.init();
        }
    }

    private isDevelopment(): boolean {
        // Check if we're in development mode
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' ||
               window.location.port === '8000';
    }

    private init(): void {
        this.connect();

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.isConnected) {
                this.connect();
            }
        });

        // Handle beforeunload to clean up
        window.addEventListener('beforeunload', () => {
            if (this.ws) {
                this.ws.close();
            }
        });
    }

    private connect(): void {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }

        const protocol: string = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl: string = `${protocol}//${window.location.host}/ws/live-reload`;

        try {
            this.ws = new WebSocket(wsUrl);
            this.setupWebSocketHandlers();
        } catch (error) {
            console.error('Live reload: Connection failed:', error);
            this.scheduleReconnect();
        }
    }

    private setupWebSocketHandlers(): void {
        if (!this.ws) return;

        this.ws.onopen = (): void => {
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
        };

        this.ws.onmessage = (event: MessageEvent): void => {
            try {
                const data: ReloadMessage = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Live reload: Failed to parse message:', error);
            }
        };

        this.ws.onclose = (event: CloseEvent): void => {
            this.isConnected = false;

            if (!this.isReloading) {
                this.scheduleReconnect();
            }
        };

        this.ws.onerror = (error: Event): void => {
            console.error('Live reload: WebSocket error:', error);
        };
    }

    private handleMessage(data: ReloadMessage): void {
        if (data.type === 'reload') {
            console.log(`Live reload: Reloading due to ${data.file}`);
            this.reload();
        }
    }

    private reload(): void {
        if (this.isReloading) {
            return;
        }

        this.isReloading = true;

        // Add a small delay to ensure the file change is complete
        setTimeout(() => {
            window.location.reload();
        }, 100);
    }

    private scheduleReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Live reload: Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay: number = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        setTimeout(() => {
            if (!this.isConnected && !this.isReloading) {
                this.connect();
            }
        }, delay);
    }
}

// Initialize live reload when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new LiveReloadClient();
    });
} else {
    new LiveReloadClient();
} 