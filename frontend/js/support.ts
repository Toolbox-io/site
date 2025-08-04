(() => {
    interface ChatRequest {
        message: string;
        session_id: string;
    }
    
    interface ChatResponse {
        content: string;
    }
    
    class SupportChat {
        private messageInput: HTMLInputElement;
        private sendButton: HTMLButtonElement;
        private responseDiv: HTMLDivElement;
        private apiUrl: string;
    
        constructor() {
            this.messageInput = document.getElementById('messageInput') as HTMLInputElement;
            this.sendButton = document.getElementById('sendButton') as HTMLButtonElement;
            this.responseDiv = document.getElementById('response') as HTMLDivElement;
            this.apiUrl = 'http://localhost:8003/chat';
            
            this.initializeEventListeners();
        }
    
        private initializeEventListeners(): void {
            this.sendButton.addEventListener('click', () => this.sendMessage());
            this.messageInput.addEventListener('keypress', (e: KeyboardEvent) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
    
        private async sendMessage(): Promise<void> {
            const message = this.messageInput.value.trim();
            if (!message) return;
    
            // Disable input and button
            this.messageInput.disabled = true;
            this.sendButton.disabled = true;
            this.responseDiv.textContent = 'Loading...';
            this.responseDiv.className = 'loading';
    
            try {
                const response = await fetch(this.apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: 'support-session'
                    } as ChatRequest)
                });
    
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const reader = response.body?.getReader();
                if (!reader) {
                    throw new Error('No response body reader available');
                }
    
                const decoder = new TextDecoder();
                let fullResponse = '';
    
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');
    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data: ChatResponse = JSON.parse(line.slice(6));
                                if (data.content) {
                                    fullResponse += data.content;
                                    this.responseDiv.textContent = fullResponse;
                                    this.responseDiv.className = '';
                                }
                            } catch (e) {
                                console.error('Error parsing SSE data:', e);
                            }
                        }
                    }
                }
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                this.responseDiv.textContent = `Error: ${errorMessage}`;
                this.responseDiv.className = '';
            } finally {
                // Re-enable input and button
                this.messageInput.disabled = false;
                this.sendButton.disabled = false;
                this.messageInput.value = '';
                this.messageInput.focus();
            }
        }
    }
    
    
    // Check if iframe parameter is set to true
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('iframe') === 'true') {
        document.body.classList.add('iframe');
    }
    
    new SupportChat();
})();