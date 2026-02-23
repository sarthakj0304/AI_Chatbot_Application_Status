import { useState } from "react";
import ChatBubble from "../components/ChatBubble";
import ChatInput from "../components/ChatInput";
import LeadModal from "../components/LeadModal";
import { sendMessage } from "../api/api";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [showLead, setShowLead] = useState(false);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    const res = await sendMessage(input);

    const botMsg = { role: "bot", text: res.answer };
    setMessages((prev) => [...prev, botMsg]);

    setLoading(false);

    if (input.toLowerCase().includes("interested")) {
      setShowLead(true);
    }

    setInput("");
  };

  return (
    <div className="flex-1 flex flex-col items-center px-6 py-8">
      <div className="w-full max-w-3xl flex flex-col gap-4 mb-6">
        {messages.map((m, i) => (
          <ChatBubble key={i} role={m.role} text={m.text} />
        ))}

        {loading && (
          <div className="glass px-4 py-2 rounded-2xl w-fit">Typing...</div>
        )}
      </div>

      <div className="w-full max-w-3xl">
        <ChatInput input={input} setInput={setInput} send={send} />
      </div>

      {showLead && <LeadModal close={() => setShowLead(false)} />}

      <div className="flex justify-center mt-4">
        <button
          onClick={() => setShowLead(true)}
          className="bg-emerald-600 hover:bg-emerald-500 px-6 py-2 rounded-xl transition"
        >
          I'm Interested
        </button>
      </div>
    </div>
  );
}
