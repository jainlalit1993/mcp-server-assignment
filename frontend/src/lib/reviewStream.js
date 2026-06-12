// Opens the /review SSE stream and yields each parsed event.
// EventSource can't POST, so we read the response body ourselves and split on the
// SSE "data:" frames.

export async function* streamReview({ repoUrl, question, signal }) {
  const res = await fetch("/review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl, question }),
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`Server responded ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  // SSE events are separated by a blank line. Different servers use different
  // line endings (sse-starlette uses CRLF), so split on every variant.
  const FRAME = /\r\n\r\n|\n\n|\r\r/;
  const LINE = /\r\n|\n|\r/;

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const frames = buffer.split(FRAME);
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const dataLines = frame
        .split(LINE)
        .filter((l) => l.startsWith("data:"))
        .map((l) => l.replace(/^data:\s?/, ""));
      if (dataLines.length === 0) continue; // keep-alive / comment frame
      try {
        yield JSON.parse(dataLines.join("\n"));
      } catch {
        // ignore malformed frames
      }
    }
  }
}
