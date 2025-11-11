/**
 * TypeScript types and interfaces for AutoWeb Outreach AI
 */

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  password_confirm: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Business Types
// ============================================================================

export interface Business {
  id: string;
  name: string;
  category?: string;
  location?: string;
  address?: string;
  phone?: string;
  email?: string;
  website_url?: string;
  description?: string;
  score: number | null;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
}

export interface BusinessCreate {
  name: string;
  category?: string;
  location?: string;
  address?: string;
  phone?: string;
  email?: string;
  website_url?: string;
  description?: string;
}

export interface BusinessUpdate {
  name?: string;
  category?: string;
  location?: string;
  address?: string;
  phone?: string;
  email?: string;
  website_url?: string;
  description?: string;
}

export interface BusinessListParams {
  limit?: number;
  offset?: number;
  location?: string;
  category?: string;
  score_min?: number;
  score_max?: number;
  search?: string;
}

export interface PaginatedBusinessResponse {
  items: Business[];
  total: number;
  limit: number;
  offset: number;
}

export interface BusinessDiscoveryRequest {
  location: string;
  category: string;
  max_results?: number;
  auto_evaluate?: boolean;
}

export interface BusinessDiscoveryResponse {
  discovered: number;
  saved: number;
  evaluated: number;
  templates_generated: number;
  businesses: Business[];
}

// ============================================================================
// Evaluation Types
// ============================================================================

export interface Evaluation {
  id: string;
  business_id: string;
  performance_score: number | null;
  seo_score: number | null;
  accessibility_score: number | null;
  aggregate_score: number;
  evaluated_at: string;
  created_at: string;
}

export interface EvaluationWithProblems extends Evaluation {
  problems: Problem[];
}

export interface Problem {
  id: string;
  evaluation_id: string;
  category: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  recommendation: string;
}

// ============================================================================
// Template Types
// ============================================================================

export interface Template {
  id: string;
  business_id: string;
  variant_number: number;
  html_content: string;
  css_content?: string;
  improvements_made: Improvement[];
  generated_at: string;
}

export interface Improvement {
  category: string;
  description: string;
  impact: 'low' | 'medium' | 'high';
}

// ============================================================================
// Scraping Job Types
// ============================================================================

export interface ScrapingJob {
  id: string;
  location: string;
  category: string;
  max_results: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  businesses_found: number;
  created_at: string;
  completed_at?: string;
  error?: string;
}

export interface ScrapingJobCreate {
  location: string;
  category: string;
  max_results?: number;
}

// ============================================================================
// Stats Types
// ============================================================================

export interface Stats {
  total_businesses: number;
  qualified_leads: number;
  templates_generated: number;
}

export interface HealthCheck {
  status: string;
  version: string;
  environment: string;
  timestamp: string;
  database: string;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
    request_id?: string;
  };
}
