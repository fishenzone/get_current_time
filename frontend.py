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
<html>
<head>
    <title>LangGraph Time Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        #chat-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            height: 500px;
            overflow-y: auto;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user {
            background-color: #e3f2fd;
            text-align: right;
        }
        .assistant {
            background-color: #f5f5f5;
            text-align: left;
        }
        #input-container {
            display: flex;
            gap: 10px;
        }
        #message-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        #send-button {
            padding: 10px 20px;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        #send-button:hover {
            background-color: #1976D2;
        }
        h1 {
            text-align: center;
            color: #333;
        }
    </style>
</head>
<body>
    <h1>🤖 LangGraph Time Bot</h1>
    <div id="chat-container"></div>
    <div id="input-container">
        <input type="text" id="message-input" placeholder="Ask me anything... Try 'What time is it?'" />
        <button id="send-button">Send</button>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');

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
            }
        }

        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Initial message
        addMessage("Hello! I'm a time-aware assistant. Ask me 'What time is it?' to see my tool in action!", false);
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
