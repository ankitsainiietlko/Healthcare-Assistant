import { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function Chatbot() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [location, setLocation] = useState(null); // ✅ GPS-based location only (Removed manual city input)

  const chatContainerRef = useRef(null);

  // ✅ Fetch user location (GPS)
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          });
        },
        (error) => {
          console.error("❌ Location access denied:", error);
          setLocation(null);
        }
      );
    }
  }, []);

  // ✅ Send message to AI
  const sendMessage = async () => {
    if (!message.trim()) return;

    setChatHistory((prev) => [...prev, { sender: "User", text: message }]);

    try {
      const res = await axios.post("https://healthcare-assistant-b1ml.onrender.com/chat/", {
        prompt: message,
        latitude: location?.lat, // ✅ GPS location (if available)
        longitude: location?.lon,
      });

      setChatHistory((prev) => [...prev, { sender: "AI", text: res.data.response }]);
    } catch (error) {
      console.error("❌ API Error:", error);
      setChatHistory((prev) => [...prev, { sender: "AI", text: "❌ Error connecting to AI. Please try again." }]);
    }

    setMessage("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col items-center w-full h-full">
      <div
        ref={chatContainerRef}
        className="w-full max-w-3xl h-96 overflow-y-auto p-4 border rounded-md dark:border-gray-700 dark:bg-gray-800 border-gray-300 bg-gray-100"
      >
        {chatHistory.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === "User" ? "justify-end" : "justify-start"}`}>
            <div
              className={`p-3 rounded-lg m-1 max-w-xs text-sm ${
                msg.sender === "User"
                  ? "bg-blue-500 text-white"
                  : "dark:bg-gray-700 dark:text-gray-200 bg-gray-300 text-black"
              }`}
            >
              <strong className="text-xs">{msg.sender}:</strong> {msg.text}
            </div>
          </div>
        ))}
      </div>

      <div className="flex mt-4 w-full max-w-3xl">
        <input
          type="text"
          className="flex-grow p-2 border rounded-l-md focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white border-gray-300 bg-gray-100 text-black"
          placeholder="Type a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-r-md hover:bg-blue-600 transition"
          onClick={sendMessage}
        >
          Send 🚀
        </button>
      </div>
    </div>
  );
}
