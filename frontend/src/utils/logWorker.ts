import { LogEntry } from "./logger";

// Process log entries in a separate thread
self.onmessage = (event: MessageEvent) => {
  try {
    if (!event.data || event.data.type !== "process" || !event.data.entry) {
      // Invalid message structure
      self.postMessage({
        type: "error",
        error: "Malformed log entry or message type.",
      });
      return;
    }
    const entry: LogEntry = event.data.entry;
    // Optionally validate entry fields here
    // Send the processed entry back
    self.postMessage({
      type: "processed",
      entry,
    });
  } catch (err) {
    // Log error and prevent worker from crashing
    self.postMessage({
      type: "error",
      error: (err as Error).message || "Unknown error in log worker.",
    });
  }
};
