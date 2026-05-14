import { useState } from "react";
import { sendLead } from "../api/api";

export default function LeadModal({ close }) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");

  const submit = async () => {
    await sendLead(email, role);
    close();
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="glass p-6 rounded-2xl w-96">
        <h2 className="text-lg font-semibold mb-4">Interested? Apply Now</h2>

        <input
          className="w-full mb-3 p-3 rounded-xl bg-white/5 border border-white/10"
          placeholder="Your Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="w-full mb-4 p-3 rounded-xl bg-white/5 border border-white/10"
          placeholder="Preferred Role"
          onChange={(e) => setRole(e.target.value)}
        />

        <button
          onClick={submit}
          className="w-full bg-indigo-600 hover:bg-indigo-500 py-2 rounded-xl"
        >
          Submit
        </button>
      </div>
    </div>
  );
}
