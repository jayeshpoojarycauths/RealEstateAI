import axios, { AxiosInstance } from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// Log levels
export enum LogLevel {
  DEBUG = "DEBUG",
  INFO = "INFO",
  WARN = "WARN",
  ERROR = "ERROR",
}

// Log entry interface
export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  logger: string;
  message: string;
  module?: string;
  function?: string;
  line?: number;
  name?: string;
  msg?: string;
  args?: any[];
  levelname?: string;
  levelno?: number;
  pathname?: string;
  filename?: string;
  exc_info?: any;
  exc_text?: string;
  stack_info?: string;
  lineno?: number;
  funcName?: string;
  created?: number;
  msecs?: number;
  relativeCreated?: number;
  thread?: number;
  threadName?: string;
  processName?: string;
  process?: number;
  taskName?: string;
  message_code?: string;
  message_type?: string;
  log_message?: string;
  method?: string;
  path?: string;
  status_code?: number;
  process_time?: number;
  request_id?: string;
  client_ip?: string;
  url?: string;
  service?: string;
  correlation_id?: string;
}

// Log batch interface
export interface LogBatch {
  entries: LogEntry[];
}

interface LoggerConfig {
  apiEndpoint: string;
  maxBufferSize: number;
  flushInterval: number;
  maxRetries: number;
  retryDelay: number;
  maxWorkers: number;
  isDevelopment: boolean;
}

const DEFAULT_CONFIG: LoggerConfig = {
  apiEndpoint: `${API_BASE_URL}/logs`,
  maxBufferSize: 100,
  flushInterval: 5000,
  maxRetries: 3,
  retryDelay: 1000,
  maxWorkers: 4,
  isDevelopment: import.meta.env.MODE === "development",
};

export class Logger {
  private static instance: Logger;
  private buffer: LogEntry[] = [];
  private readonly config: LoggerConfig;
  private flushTimer: number | null = null;
  private readonly axiosInstance: AxiosInstance;
  private readonly workerPool: Worker[];
  private isShuttingDown: boolean = false;

  private constructor() {
    this.config = { ...DEFAULT_CONFIG };
    this.axiosInstance = axios.create({
      timeout: 5000,
      headers: {
        "Content-Type": "application/json",
      },
    });
    this.workerPool = this.createWorkerPool();
    this.startFlushTimer();
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private createWorkerPool(): Worker[] {
    const workers: Worker[] = [];
    for (let i = 0; i < this.config.maxWorkers; i++) {
      const worker = new Worker(new URL("./logWorker.ts", import.meta.url));
      worker.onerror = (error) => {
        console.error(`Log worker error: ${error.message}`);
      };
      workers.push(worker);
    }
    return workers;
  }

  private startFlushTimer(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    this.flushTimer = setInterval(
      () => this.flush(),
      this.config.flushInterval,
    );
  }

  private createLogEntry(
    level: LogLevel,
    message: string,
    context: Record<string, any> = {},
  ): LogEntry {
    const timestamp = new Date().toISOString();
    return {
      timestamp,
      level,
      logger: "frontend",
      message,
      service: context.service || "frontend",
      correlation_id: context.correlationId,
      created: Date.now(),
      msecs: new Date().getMilliseconds(),
      relativeCreated: performance.now(),
      thread: 0,
      threadName: "main",
      processName: "browser",
      process: 0,
      taskName: "main",
      ...context,
    };
  }

  private async flush(): Promise<void> {
    if (this.buffer.length === 0 || this.isShuttingDown) return;

    const batch: LogBatch = {
      entries: [...this.buffer],
    };
    this.buffer = [];

    let retries = 0;
    while (retries < this.config.maxRetries) {
      try {
        await this.axiosInstance.post(this.config.apiEndpoint, batch);
        break;
      } catch (error) {
        retries++;
        if (retries === this.config.maxRetries) {
          console.error(
            "Failed to send logs to server after max retries:",
            error,
          );
          // Put logs back in buffer if they couldn't be sent
          this.buffer = [...batch.entries, ...this.buffer];
        } else {
          await new Promise((resolve) =>
            setTimeout(resolve, this.config.retryDelay * retries),
          );
        }
      }
    }
  }

  private log(level: LogLevel, message: string, data?: any): void {
    const logEntry = this.createLogEntry(level, message, data);

    if (this.config.isDevelopment) {
      switch (level) {
        case LogLevel.DEBUG:
          console.debug(logEntry);
          break;
        case LogLevel.INFO:
          console.info(logEntry);
          break;
        case LogLevel.WARN:
          console.warn(logEntry);
          break;
        case LogLevel.ERROR:
          console.error(logEntry);
          break;
      }
    }

    this.buffer.push(logEntry);
    this.checkBuffer();
  }

  public debug(message: string, data?: any): void {
    this.log(LogLevel.DEBUG, message, data);
  }

  public info(message: string, data?: any): void {
    this.log(LogLevel.INFO, message, data);
  }

  public warn(message: string, data?: any): void {
    this.log(LogLevel.WARN, message, data);
  }

  public error(message: string, data?: any): void {
    this.log(LogLevel.ERROR, message, data);
  }

  private checkBuffer(): void {
    if (this.buffer.length >= this.config.maxBufferSize) {
      this.flush();
    }
  }

  public async shutdown(): Promise<void> {
    this.isShuttingDown = true;

    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }

    // Stop all workers
    for (const worker of this.workerPool) {
      worker.terminate();
    }

    // Final flush
    await this.flush();
  }
}

// Create default logger instance
export const logger = Logger.getInstance();

// Export default for convenience
export default logger;
