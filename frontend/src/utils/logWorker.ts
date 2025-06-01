import { LogEntry } from './logger';

// Process log entries in a separate thread
self.onmessage = (event: MessageEvent) => {
    if (event.data.type === 'process') {
        const entry: LogEntry = event.data.entry;
        
        // Add any additional processing here
        // For example, you could:
        // - Add environment information
        // - Add browser/device information
        // - Add performance metrics
        // - Add memory usage
        // - Add network status
        
        // Send the processed entry back
        self.postMessage({
            type: 'processed',
            entry
        });
    }
}; 