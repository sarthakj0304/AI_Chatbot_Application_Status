const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5001";

export const sendMessage = async (query) => {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  return res.json();
};

export const sendLead = async (email, role) => {
  await fetch(`${API_URL}/lead`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role }),
  });
};

export const getLogs = async () => {
  const res = await fetch(`${API_URL}/admin/logs`);
  return res.json();
};

export const getStats = async () => {
  const res = await fetch(`${API_URL}/admin/stats`);
  return res.json();
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  
  const res = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  return res.json();
};

export const getDocuments = async () => {
  const res = await fetch(`${API_URL}/admin/documents`);
  return res.json();
};

export const getAnalytics = async () => {
  const res = await fetch(`${API_URL}/admin/analytics`);
  return res.json();
};
