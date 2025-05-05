import React, { useState } from "react";
import axios from "axios";

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { sender: "user", text: input };
        setMessages([...messages, userMessage]);

        try {
            const response = await axios.post("/api/query-ollama", { message: input });
            setMessages([...messages, userMessage, { sender: "bot", text: response.data.reply }]);
        } catch (error) {
            console.error("Error:", error);
        }

        setInput("");
    };

    const uploadFile = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("http://localhost:5000/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setMessages([...messages, { sender: "system", text: `File uploaded: ${response.data.filename}` }]);
        } catch (error) {
            console.error("Error uploading file:", error);
        }
    };

    return (
        <div style={{ width: "400px", margin: "auto", textAlign: "center" }}>
            <div style={{ height: "300px", border: "1px solid black", overflowY: "auto", padding: "10px" }}>
                {messages.map((msg, index) => (
                    <div key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left" }}>
                        <strong>{msg.sender === "user" ? "You" : "OLLAMA"}:</strong> {msg.text}
                    </div>
                ))}
            </div>

            {/* שדה קלט וכפתור לשליחת הודעה */}
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} />
            <button onClick={sendMessage}>Send</button>

            {/* כפתור העלאת קובץ */}
            <div style={{ marginTop: "10px" }}>
                <input type="file" onChange={uploadFile} />
            </div>
        </div>
    );
};

export default Chat;
