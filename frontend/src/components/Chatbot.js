// Sample React component for chatbot UI
import { useEffect, useState } from "react";

const Chatbot = (username) => {
  const AIAssistant = "ai-assistant";
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const startupMessage = {
    sender: AIAssistant,
    text: "Hello, ask me anything",
  };
  const [chatHistory, setChatHistory] = useState([startupMessage]);

  const addMessageToHistory = (sender, message) => {
    console.log(`Add to chat history: ${message}`);
    setChatHistory((prevHistory) => [
      ...prevHistory,
      { sender: sender, text: message },
    ]);
  };

  const handleSendMessage = async () => {
    // Update message history + clean text box
    console.log(`Sending user query ${query} to backend`);
    addMessageToHistory(username, query);

    // Fetch response from backend
    setResponse("...");
    // const apiResponse = await fetch(`/chatbot/${query}`);
    const requestBody = JSON.stringify({ query: query });
    const apiResponse = await fetch("http://localhost:8000/chatbot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: requestBody,
    });

    setQuery("");
    const result = await apiResponse.json();
    setResponse(result.response);
    addMessageToHistory(AIAssistant, result.response);
  };

  useEffect(() => {
    // Connect to the backend WebSocket (FastAPI)
    // Listen for incoming messages and update the messages state
  }, []);

  const chatWindowStyle = {
    height: "400px",
    overflowY: "scroll",
    border: "1px solid #ccc",
    padding: "10px",
  };

  const messageStyle = {
    marginBottom: "10px",
    padding: "5px",
    borderRadius: "8px",
  };

  const userMessageStyle = {
    backgroundColor: "#e6f7ff",
    textAlign: "right",
  };

  const assistantMessageStyle = {
    backgroundColor: "#f0f0f0",
    textAlign: "left",
  };

  return (
    <div>
      <div>AI Assistant</div>

      {/* Display chat history */}
      <div style={chatWindowStyle}>
        {chatHistory.map((message, index) => (
          <div
            key={index}
            style={{
              ...messageStyle,
              ...(message.sender === AIAssistant
                ? assistantMessageStyle
                : userMessageStyle),
            }}
          >
            {message.sender === username
              ? `${message.text} 😁`
              : `🤖 ${message.text}`}
          </div>
        ))}
      </div>

      {/* User input form */}
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSendMessage}>Send</button>
    </div>
  );
};

export default Chatbot;
