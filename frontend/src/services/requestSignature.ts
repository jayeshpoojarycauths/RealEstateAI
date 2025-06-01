import { api } from "./api";
import { logger } from "../utils/logger";

/**
 * Request signature service for protecting critical actions
 * Implements replay protection and request signing
 */
export class RequestSignatureService {
  private static instance: RequestSignatureService;
  private nonceCache: Set<string> = new Set();
  private readonly NONCE_EXPIRY = 5 * 60 * 1000; // 5 minutes

  private constructor() {
    // Clean up expired nonces every minute
    setInterval(() => this.cleanupNonces(), 60 * 1000);

    // Attach interceptor immediately
    this.setupRequestInterceptor();
  }

  public static getInstance(): RequestSignatureService {
    if (!RequestSignatureService.instance) {
      RequestSignatureService.instance = new RequestSignatureService();
    }
    return RequestSignatureService.instance;
  }

  /**
     * Generate a unique nonce for request signing
private nonceCache: Map<string, number> = new Map();
 ...
 const nonce = crypto.randomUUID();
this.nonceCache.set(nonce, Date.now());
        return nonce;
    }

    /**
     * Clean up expired nonces
     */
  private cleanupNonces(): void {
    const now = Date.now();
    for (const nonce of this.nonceCache) {
      if (now - parseInt(nonce.split("-")[0]) > this.NONCE_EXPIRY) {
        this.nonceCache.delete(nonce);
      }
    }
  }

  /**
   * Sign a request with a nonce and timestamp
   * @param method - HTTP method
   * @param url - Request URL
   * @param data - Request data
   */
  public async signRequest(
    method: string,
    url: string,
    data?: any,
  ): Promise<{
    signature: string;
    nonce: string;
    timestamp: number;
  }> {
    const timestamp = Date.now();
    const nonce = this.generateNonce();
    const token = localStorage.getItem("token");

    if (!token) {
      throw new Error("No authentication token found");
    }

    // Create signature payload
    const payload = {
      method,
      url,
      data,
      nonce,
      timestamp,
    };

    // Sign the payload using HMAC-SHA256
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(token),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );

    const signature = await crypto.subtle.sign(
      "HMAC",
      key,
      encoder.encode(JSON.stringify(payload)),
    );

    return {
      signature: btoa(String.fromCharCode(...new Uint8Array(signature))),
      nonce,
      timestamp,
    };
  }

  /**
   * Add request signature to axios interceptor
   */
  public setupRequestInterceptor(): void {
    api.interceptors.request.use(
      async (config) => {
        // Only sign critical actions
        if (
          ["POST", "PUT", "DELETE"].includes(config.method?.toUpperCase() || "")
        ) {
          try {
            const { signature, nonce, timestamp } = await this.signRequest(
              config.method?.toUpperCase() || "",
              config.url || "",
              config.data,
            );

            config.headers = {
              ...config.headers,
              "X-Request-Signature": signature,
              "X-Request-Nonce": nonce,
              "X-Request-Timestamp": timestamp.toString(),
            };
          } catch (error) {
            logger.error("Failed to sign request", error);
          }
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      },
    );
  }
}

// Export singleton instance
export const requestSignature = RequestSignatureService.getInstance();
