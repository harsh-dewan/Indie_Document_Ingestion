"use client";

import { useState, useRef, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Role = "user" | "assistant";

type Message = {
  role: Role;
  content: string;
};

type Session = {
  doc_id: string;
  strategy_name: string;
  filename: string;
};

export default function Home() {
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/ingest`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");

      setSession({ doc_id: data.doc_id, strategy_name: data.strategy_name, filename: data.filename });
      setMessages([]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleSend() {
    if (!input.trim() || !session || loading) return;

    const query = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          doc_id: session.doc_id,
          strategy_name: session.strategy_name,
          top_k: 5,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Chat failed");

      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-col h-screen max-w-3xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">Document Chat</h1>
        {session && (
          <label className="cursor-pointer text-sm text-blue-600 hover:underline">
            Upload new
            <input
              ref={fileRef}
              type="file"
              className="hidden"
              accept=".pdf,.docx,.txt,.md"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
        )}
      </div>

      {/* Upload area — shown only when no session */}
      {!session && (
        <label className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl py-16 cursor-pointer transition-colors ${uploading ? "border-blue-300 bg-blue-50" : "border-gray-300 hover:border-blue-400 hover:bg-blue-50"}`}>
          {uploading ? (
            <p className="text-blue-500 font-medium">Processing document…</p>
          ) : (
            <>
              <p className="text-gray-500 mb-3">Drop a file or click to upload</p>
              <span className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg">Choose file</span>
              <p className="text-xs text-gray-400 mt-3">Supported: PDF, DOCX, TXT, MD</p>
            </>
          )}
          <input
            ref={fileRef}
            type="file"
            className="hidden"
            accept=".pdf,.docx,.txt,.md"
            onChange={handleUpload}
            disabled={uploading}
          />
        </label>
      )}

      {/* Active document badge */}
      {session && (
        <div className="flex items-center gap-2 mb-3 px-3 py-2 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">
          <span>✓</span>
          <span className="font-medium truncate">{session.filename}</span>
        </div>
      )}

      {/* Error banner */}
      {error && (
        <div className="mb-3 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      {/* Messages */}
      {session && (
        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
          {messages.length === 0 && (
            <p className="text-center text-gray-400 text-sm mt-12">
              Ask anything about <span className="font-medium">{session.filename}</span>
            </p>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap leading-relaxed ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-br-sm"
                    : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                <span className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      {/* Input bar */}
      {session && (
        <div className="flex gap-2 mt-auto">
          <input
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:opacity-50 bg-white"
            placeholder="Ask a question…"
            value={input}
            disabled={loading}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          />
          <button
            className="px-5 py-2.5 bg-blue-600 text-white text-sm rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors"
            disabled={loading || !input.trim()}
            onClick={handleSend}
          >
            Send
          </button>
        </div>
      )}
    </main>
  );
}
