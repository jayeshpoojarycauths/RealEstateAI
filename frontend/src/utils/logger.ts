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
  level: LogLevel;
  message: string;
  timestamp: string;
  context: Record<string, any>;
  stackTrace?: string;
  service?: string;
  correlationId?: string;
}

// Log batch interface
export interface LogBatch {
  entries: LogEntry[];
}

export interface AuditLogEntry extends LogEntry {
  action: string;
  resourceType: string;
  resourceId: string | number;
  userId?: string;
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
    stackTrace?: string,
  ): LogEntry {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      context: this.sanitizeContext(context),
      stackTrace,
      service: context.service || "frontend",
      correlationId: context.correlationId,
    };
  }

  private sanitizeContext(context: Record<string, any>): Record<string, any> {
    const sanitized: Record<string, any> = {};
    const sensitivePatterns = [
      /password/i,
      /api[_-]?key/i,
      /token/i,
      /secret/i,
      /authorization/i,
      /credit[_-]?card/i,
      /ssn/i,
      /social[_-]?security/i,
    ];

    for (const [key, value] of Object.entries(context)) {
      if (
        typeof value === "string" &&
        sensitivePatterns.some((pattern) => pattern.test(key))
      ) {
        sanitized[key] = "***";
      } else if (typeof value === "object" && value !== null) {
        sanitized[key] = this.sanitizeContext(value);
      } else {
        sanitized[key] = value;
      }
    }

    return sanitized;
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

  private formatMessage(
    level: LogLevel,
    message: string,
    data?: any,
  ): LogEntry {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      context:
        data && typeof data === "object" ? this.sanitizeContext(data) : {},
      stackTrace: undefined,
      service: (data && data.service) || "frontend",
      correlationId: data && data.correlationId,
    };
  }

  private log(level: LogLevel, message: string, data?: any): void {
    const logMessage = this.formatMessage(level, message, data);

    if (this.config.isDevelopment) {
      switch (level) {
        case LogLevel.DEBUG:
          console.debug(logMessage);
          break;
        case LogLevel.INFO:
          console.info(logMessage);
          break;
        case LogLevel.WARN:
          console.warn(logMessage);
          break;
        case LogLevel.ERROR:
          console.error(logMessage);
          break;
      }
    } else {
      // In production, you might want to send logs to a service like Sentry
      if (level === LogLevel.ERROR) {
        // Example: Sentry.captureException(data);
      }
    }
    // Always add to buffer for persistence and backend delivery
    this.buffer.push(logMessage);
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

  public audit(
    action: string,
    resourceType: string,
    resourceId: string | number,
    userId?: string,
    context: Record<string, any> = {},
  ): void {
    const auditEntry: AuditLogEntry = {
      ...this.createLogEntry(
        LogLevel.INFO,
        `Audit: ${action} ${resourceType} ${resourceId}`,
        context,
      ),
      action,
      resourceType,
      resourceId,
      userId,
    };
    this.buffer.push(auditEntry);
    this.checkBuffer();
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
