from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from langchain_core.messages import HumanMessage
from app import graph

app = FastAPI()

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Time Bot</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #6C63FF; /* Vibrant Purple */
            --primary-light: #8E88FF;
            --secondary-color: #00BFA5; /* Teal */
            --background-gradient-start: #ECE9F6;
            --background-gradient-end: #E0F2F7;
            --card-background: #ffffff;
            --user-bubble: #F1F1F1; /* Light Gray */
            --assistant-bubble: #EBF7FF; /* Light Blue */
            --border-color: #F0F0F0;
            --text-color: #2C3E50; /* Dark Blue-Gray */
            --light-text-color: #7F8C8D;
            --shadow-light: 0 4px 8px rgba(0,0,0,0.05);
            --shadow-medium: 0 8px 24px rgba(0,0,0,0.1);
            --border-radius-card: 15px;
            --border-radius-bubble: 22px;
            --transition-speed: 0.3s;
        }

        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, var(--background-gradient-start), var(--background-gradient-end));
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: var(--text-color);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow: hidden; /* Prevent body scrollbar on mobile */
        }

        .container {
            width: 90%;
            max-width: 600px;
            background-color: var(--card-background);
            border-radius: var(--border-radius-card);
            box-shadow: var(--shadow-medium);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 80vh;
            max-height: 95vh;
            position: relative;
            z-index: 1;
        }

        h1 {
            text-align: center;
            color: white; /* Changed for better robot visibility */
            background: var(--primary-color); /* Changed to solid background */
            padding: 20px 0;
            margin: 0;
            font-size: 2.2em;
            font-weight: 700;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 10;
            box-shadow: var(--shadow-light);
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2); /* Added subtle text shadow */
        }

        #chat-container {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
            scroll-behavior: smooth;
            background-color: #FDFDFD;
        }

        /* Custom scrollbar */
        #chat-container::-webkit-scrollbar {
            width: 8px;
        }
        #chat-container::-webkit-scrollbar-track {
            background: var(--background-gradient-start);
            border-radius: 10px;
        }
        #chat-container::-webkit-scrollbar-thumb {
            background: var(--primary-light);
            border-radius: 10px;
        }
        #chat-container::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }

        .message {
            max-width: 85%;
            padding: 14px 20px;
            border-radius: var(--border-radius-bubble);
            word-wrap: break-word;
            line-height: 1.6;
            box-shadow: var(--shadow-light);
            transition: transform var(--transition-speed) ease-out;
        }
        .message:hover {
            transform: translateY(-2px);
        }
        .user {
            background-color: var(--user-bubble);
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }
        .assistant {
            background-color: var(--assistant-bubble);
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }
        
        #input-container {
            display: flex;
            padding: 20px;
            gap: 15px;
            border-top: 1px solid var(--border-color);
            background-color: var(--card-background);
            position: sticky;
            bottom: 0;
            z-index: 10;
        }

        #message-input {
            flex: 1;
            padding: 14px 20px;
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-card);
            font-size: 1em;
            outline: none;
            transition: border-color var(--transition-speed) ease, box-shadow var(--transition-speed) ease;
        }
        #message-input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.2);
        }
        #message-input:disabled {
            background-color: #f8f8f8;
            cursor: not-allowed;
        }

        #send-button {
            padding: 14px 28px;
            background: linear-gradient(45deg, var(--primary-color), var(--primary-light));
            color: white;
            border: none;
            border-radius: var(--border-radius-card);
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all var(--transition-speed) ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        #send-button:hover:not(:disabled) { /* Apply hover only when not disabled */
            background: linear-gradient(45deg, var(--primary-light), var(--primary-color));
            box-shadow: 0 6px 15px rgba(108, 99, 255, 0.3);
            transform: translateY(-2px);
        }
        #send-button:active:not(:disabled) { /* Apply active only when not disabled */
            transform: translateY(0);
            box-shadow: var(--shadow-light);
        }
        #send-button::after {
            content: '➤'; /* Unicode arrow */
            font-size: 1.2em;
            line-height: 1;
            margin-left: 5px;
            transform: rotate(0deg);
            transition: transform var(--transition-speed) ease;
        }
        #send-button:hover::after {
            transform: rotate(15deg);
        }
        #send-button:disabled {
            background: #CCCCCC; /* Grayed out when disabled */
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }
        #send-button:disabled::after {
            display: none; /* Hide arrow when sending */
        }


        /* Responsive adjustments */
        @media (max-width: 768px) {
            .container {
                width: 100%;
                margin: 0;
                border-radius: 0;
                min-height: 100vh;
                max-height: 100vh;
                box-shadow: none;
            }
            body {
                align-items: flex-start;
                background: var(--background-color);
            }
            #input-container {
                flex-direction: column;
                gap: 10px;
                padding: 15px;
            }
            #send-button {
                width: 100%;
                padding: 12px;
                justify-content: center;
            }
            h1 {
                font-size: 1.8em; /* Slightly smaller on mobile */
            }
            .message {
                max-width: 90%;
                padding: 10px 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 LangGraph Time Bot</h1>
        <div id="chat-container"></div>
        <div id="input-container">
            <input type="text" id="message-input" placeholder="Ask me anything... Try 'What time is it?'" />
            <button id="send-button">Send</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const originalButtonHTML = 'Send <span style="font-size: 1.2em; line-height: 1; margin-left: 5px;">➤</span>'; // Store original HTML

        function addMessage(message, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            messageDiv.textContent = message;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            addMessage(message, true);
            messageInput.value = '';

            // Disable input/button during API call
            messageInput.disabled = true;
            sendButton.disabled = true;
            sendButton.innerHTML = 'Sending...'; 

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });

                const data = await response.json();
                addMessage(data.response, false);
            } catch (error) {
                addMessage('Error: Failed to get response', false);
            } finally {
                // Re-enable input/button
                messageInput.disabled = false;
                sendButton.disabled = false;
                sendButton.innerHTML = originalButtonHTML; // Restore original HTML
                messageInput.focus(); // Keep focus on input
            }
        }

        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Initial message and set original button HTML
        addMessage("Hello! I'm a time-aware assistant. Ask me 'What time is it?' to see my tool in action!", false);
        sendButton.innerHTML = originalButtonHTML; // Set initial button content with arrow
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return html_content

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    try:
        state = {"messages": [HumanMessage(content=chat_message.message)]}
        result = await graph.ainvoke(state)
        last_message = result["messages"][-1]
        if hasattr(last_message, 'content'):
            response_text = last_message.content
        else:
            response_text = str(last_message)
        
        return ChatResponse(response=response_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)