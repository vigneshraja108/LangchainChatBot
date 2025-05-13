import { StreamingTextResponse } from "ai";
import { Message } from "ai/react";

export const runtime = "edge";

export async function POST(req: Request) {
  const { messages } = await req.json();
  const lastMessage = messages[messages.length - 1];

  const response = await fetch("http://127.0.0.1:8000/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: lastMessage.content }),
  });

  const data = await response.json();

  // Simulate a stream from the backend response
  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();
      const words = data.answer.split(" ");

      for (const word of words) {
        controller.enqueue(encoder.encode(word + " "));
        await new Promise((r) => setTimeout(r, 30));
      }

      controller.close();
    },
  });

  // This makes it compatible with useChat()
  return new StreamingTextResponse(stream);
}
