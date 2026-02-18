/**
 * ClearCause API Client
 * Handles all communication with the backend Lambda functions.
 */

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:3000";

class ClearCauseAPI {
  constructor() {
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  async _fetch(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      ...options.headers,
    };

    const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: "Unknown error" }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Upload a document for analysis.
   * @param {File} file - The PDF file to upload
   * @returns {Promise<{job_id: string, status: string}>}
   */
  async uploadDocument(file) {
    const base64 = await this._fileToBase64(file);
    return this._fetch("/api/upload", {
      method: "POST",
      body: JSON.stringify({
        fileName: file.name,
        contentType: file.type,
        file: base64,
      }),
    });
  }

  /**
   * Check the status of an analysis job.
   * @param {string} jobId
   * @returns {Promise<{job_id: string, status: string, report_key?: string}>}
   */
  async getJobStatus(jobId) {
    return this._fetch(`/api/jobs/${jobId}`);
  }

  /**
   * Get analysis results for a completed job.
   * @param {string} jobId
   * @returns {Promise<AnalysisResult>}
   */
  async getResults(jobId) {
    return this._fetch(`/api/results/${jobId}`);
  }

  /**
   * Generate and download a PDF report.
   * @param {string} jobId
   * @returns {Promise<{download_url: string}>}
   */
  async exportReport(jobId) {
    return this._fetch(`/api/report?job_id=${jobId}`);
  }

  /**
   * Poll for job completion.
   * @param {string} jobId
   * @param {function} onProgress - Called with status updates
   * @param {number} intervalMs - Polling interval
   * @param {number} timeoutMs - Maximum wait time
   * @returns {Promise<AnalysisResult>}
   */
  async waitForCompletion(jobId, onProgress = () => {}, intervalMs = 2000, timeoutMs = 120000) {
    const start = Date.now();

    while (Date.now() - start < timeoutMs) {
      const job = await this.getJobStatus(jobId);
      onProgress(job.status);

      if (job.status === "completed") {
        return this.getResults(jobId);
      }
      if (job.status === "failed") {
        throw new Error(job.error_message || "Analysis failed");
      }

      await new Promise((r) => setTimeout(r, intervalMs));
    }

    throw new Error("Analysis timed out");
  }

  _fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(",")[1]);
      reader.onerror = () => reject(new Error("Failed to read file"));
      reader.readAsDataURL(file);
    });
  }
}

export const api = new ClearCauseAPI();
export default api;
