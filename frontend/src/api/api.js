export const sendMessage = async (query) => {
  const res = await fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  return res.json();
};

export const sendLead = async (email, role) => {
  await fetch("http://127.0.0.1:5000/lead", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role }),
  });
};

export const getLogs = async () => {
  const res = await fetch("http://127.0.0.1:5000/admin/logs");
  return res.json();
};

export const getStats = async () => {
  const res = await fetch("http://127.0.0.1:5000/admin/stats");
  return res.json();
};
