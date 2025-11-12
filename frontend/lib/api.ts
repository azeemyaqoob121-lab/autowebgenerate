/**
 * API Client for AutoWeb Outreach AI
 * Centralized HTTP client with authentication and error handling
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  Business,
  BusinessCreate,
  BusinessUpdate,
  BusinessListParams,
  PaginatedBusinessResponse,
  BusinessDiscoveryRequest,
  BusinessDiscoveryResponse,
  Evaluation,
  EvaluationWithProblems,
  Template,
  ScrapingJob,
  ScrapingJobCreate,
  HealthCheck,
  Stats,
  ErrorResponse,
} from './types';
import { getToken, setToken, logout, shouldRefreshToken, getRefreshToken } from './auth';

// ============================================================================
// API Client Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    // Request interceptor - add JWT token
    this.client.interceptors.request.use(
      (config) => {
        const token = getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<ErrorResponse>) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          // Try to refresh token
          const refreshToken = getRefreshToken();
          if (refreshToken) {
            try {
              // TODO: Implement token refresh endpoint when available
              // For now, just logout
              logout();
              if (typeof window !== 'undefined') {
                window.location.href = '/login';
              }
            } catch (refreshError) {
              logout();
              if (typeof window !== 'undefined') {
                window.location.href = '/login';
              }
            }
          } else {
            logout();
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // ============================================================================
  // Authentication API
  // ============================================================================

  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/api/auth/register', data);
    if (response.data.access_token) {
      setToken(response.data.access_token);
    }
    return response.data;
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/api/auth/login', data);
    if (response.data.access_token) {
      setToken(response.data.access_token);

      // Also set token in cookie for middleware
      if (typeof window !== 'undefined') {
        document.cookie = `token=${response.data.access_token}; path=/; max-age=${60 * 60 * 24}; SameSite=Lax`;
      }
    }
    return response.data;
  }

  // ============================================================================
  // Business API
  // ============================================================================

  async getBusinesses(params?: BusinessListParams): Promise<PaginatedBusinessResponse> {
    const response = await this.client.get<PaginatedBusinessResponse>('/api/businesses', {
      params,
    });
    return response.data;
  }

  async getBusiness(id: string): Promise<Business> {
    const response = await this.client.get<Business>(`/api/businesses/${id}`);
    return response.data;
  }

  async createBusiness(data: BusinessCreate): Promise<Business> {
    const response = await this.client.post<Business>('/api/businesses', data);
    return response.data;
  }

  async updateBusiness(id: string, data: BusinessUpdate): Promise<Business> {
    const response = await this.client.put<Business>(`/api/businesses/${id}`, data);
    return response.data;
  }

  async deleteBusiness(id: string): Promise<void> {
    await this.client.delete(`/api/businesses/${id}`);
  }

  async discoverBusinesses(data: BusinessDiscoveryRequest): Promise<BusinessDiscoveryResponse> {
    const response = await this.client.post<BusinessDiscoveryResponse>('/api/businesses/discover', data, {
      timeout: 900000, // 15 minutes for discovery + evaluation + AI template generation
    });
    return response.data;
  }

  // ============================================================================
  // Evaluation API
  // ============================================================================

  async getBusinessEvaluation(businessId: string): Promise<Evaluation> {
    const response = await this.client.get<Evaluation>(`/api/businesses/${businessId}/evaluations`);
    return response.data;
  }

  async getEvaluation(id: string): Promise<Evaluation> {
    const response = await this.client.get<Evaluation>(`/api/evaluations/${id}`);
    return response.data;
  }

  async getEvaluationWithProblems(id: string): Promise<EvaluationWithProblems> {
    const [evaluation, problems] = await Promise.all([
      this.getEvaluation(id),
      this.client.get(`/api/evaluations/${id}/problems`).then((res) => res.data),
    ]);
    return {
      ...evaluation,
      problems,
    };
  }

  async triggerEvaluation(businessId: string): Promise<Evaluation> {
    const response = await this.client.post<Evaluation>('/api/evaluations', {
      business_id: businessId,
    });
    return response.data;
  }

  // ============================================================================
  // Template API
  // ============================================================================

  async getBusinessTemplates(businessId: string): Promise<Template[]> {
    const response = await this.client.get<{ templates: Template[]; total: number }>(`/api/businesses/${businessId}/templates`);
    return response.data.templates;
  }

  async generateTemplates(businessId: string, numVariants: number = 3): Promise<Template[]> {
    const response = await this.client.post<{ templates: Template[]; total: number }>(
      `/api/businesses/${businessId}/templates/generate`,
      { num_variants: numVariants },
      {
        timeout: 180000, // 3 minutes for GPT-4 template generation (30-60s per variant)
      }
    );
    return response.data.templates;
  }

  async regenerateTemplates(businessId: string, numVariants: number = 3): Promise<Template[]> {
    const response = await this.client.post<{ templates: Template[]; total: number }>(
      `/api/businesses/${businessId}/templates/regenerate`,
      { num_variants: numVariants },
      {
        timeout: 180000, // 3 minutes for GPT-4 template generation (30-60s per variant)
      }
    );
    return response.data.templates;
  }

  async getTemplate(id: string): Promise<Template> {
    const response = await this.client.get<Template>(`/api/templates/${id}`);
    return response.data;
  }

  // ============================================================================
  // Scraping Job API
  // ============================================================================

  async createScrapingJob(data: ScrapingJobCreate): Promise<ScrapingJob> {
    const response = await this.client.post<ScrapingJob>('/api/scraping-jobs', data);
    return response.data;
  }

  async getScrapingJob(id: string): Promise<ScrapingJob> {
    const response = await this.client.get<ScrapingJob>(`/api/scraping-jobs/${id}`);
    return response.data;
  }

  async getScrapingJobs(limit = 20, offset = 0): Promise<ScrapingJob[]> {
    const response = await this.client.get<ScrapingJob[]>('/api/scraping-jobs', {
      params: { limit, offset },
    });
    return response.data;
  }

  // ============================================================================
  // Health & Stats API
  // ============================================================================

  async healthCheck(): Promise<HealthCheck> {
    const response = await this.client.get<HealthCheck>('/api/health');
    return response.data;
  }

  async getStats(): Promise<Stats> {
    const response = await this.client.get<Stats>('/api/stats');
    return response.data;
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const api = new APIClient();
export default api;
