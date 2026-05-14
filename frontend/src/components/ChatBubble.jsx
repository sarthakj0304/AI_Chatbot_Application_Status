export default function ChatBubble({ role, text }) {
  return (
    <div
      className={`max-w-md px-4 py-3 rounded-2xl text-sm ${
        role === "user" ? "ml-auto glass bg-indigo-600/40" : "glass"
      }`}
    >
      {text}
    </div>
  );
}
