export const sendMessage = async (query) => {
  const res = await fetch(
    "https://ai-chatbot-application-status.onrender.com/chat",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    },
  );
  return res.json();
};

export const sendLead = async (email, role) => {
  await fetch("https://ai-chatbot-application-status.onrender.com/lead", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role }),
  });
};

export const getLogs = async () => {
  const res = await fetch(
    "https://ai-chatbot-application-status.onrender.com/admin/logs",
  );
  return res.json();
};

export const getStats = async () => {
  const res = await fetch(
    "https://ai-chatbot-application-status.onrender.com/admin/stats",
  );
  return res.json();
};
