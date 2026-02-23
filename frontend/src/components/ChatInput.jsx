export default function ChatInput({ input, setInput, send }) {
  return (
    <div className="glass p-4 flex gap-3 rounded-2xl">
      <input
        className="flex-1 bg-transparent outline-none text-white"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about roles, benefits, interview process..."
      />
      <button
        onClick={send}
        className="bg-indigo-600 hover:bg-indigo-500 px-5 py-2 rounded-xl transition"
      >
        Send
      </button>
    </div>
  );
}
