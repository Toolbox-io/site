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

        private addMessage(content: string, type: 'user' | 'bot'): void {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = content;
            this.responseDiv.appendChild(messageDiv);
            this.responseDiv.scrollTop = this.responseDiv.scrollHeight;
        }

        private showTypingIndicator(): void {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message typing';
            typingDiv.textContent = 'Typing';
            typingDiv.id = 'typing-indicator';
            this.responseDiv.appendChild(typingDiv);
            this.responseDiv.scrollTop = this.responseDiv.scrollHeight;
        }

        private hideTypingIndicator(): void {
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }

        private updateBotMessage(content: string, botMessageDiv: HTMLDivElement): void {
            // Format markdown if available
            if (typeof (window as any).marked !== 'undefined') {
                botMessageDiv.innerHTML = (window as any).marked.parse(content);
            } else {
                botMessageDiv.textContent = content;
            }
            
            this.responseDiv.scrollTop = this.responseDiv.scrollHeight;
        }

        private async sendMessage(): Promise<void> {
            const message = this.messageInput.value.trim();
            if (!message) return;

            // Add user message
            this.addMessage(message, 'user');

            // Disable input and button
            this.messageInput.disabled = true;
            this.sendButton.disabled = true;

            // Show typing indicator
            this.showTypingIndicator();

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

                // Hide typing indicator and start bot message
                this.hideTypingIndicator();
                const botMessageDiv = document.createElement('div');
                botMessageDiv.className = 'message bot-message';
                this.responseDiv.appendChild(botMessageDiv);

                const reader = response.body?.getReader();
                if (!reader) {
                    throw new Error('No response body reader available');
                }

                const decoder = new TextDecoder();
                let fullResponse = '';
                let accumulatedText = '';

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
                                    accumulatedText += data.content;
                                    
                                    // Update the bot message with accumulated content
                                    this.updateBotMessage(accumulatedText, botMessageDiv);
                                }
                            } catch (e) {
                                console.error('Error parsing SSE data:', e);
                            }
                        }
                    }
                }
            } catch (error) {
                this.hideTypingIndicator();
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                this.addMessage(`Error: ${errorMessage}`, 'bot');
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