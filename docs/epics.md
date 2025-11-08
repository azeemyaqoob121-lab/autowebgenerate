# AutoWeb_Outreach_AI - Epic Breakdown

**Author:** azeem yaqoob
**Date:** 2025-10-31
**Project Level:** 3
**Target Scale:** Medium-scale web platform (42-54 stories)

---

## Overview

This document provides the detailed epic breakdown for AutoWeb_Outreach_AI, expanding on the high-level epic list in the [PRD](./PRD.md).

Each epic includes:

- Expanded goal and value proposition
- Complete story breakdown with user stories
- Acceptance criteria for each story
- Story sequencing and dependencies

**Epic Sequencing Principles:**

- Epic 1 establishes foundational infrastructure and initial functionality
- Subsequent epics build progressively, each delivering significant end-to-end value
- Stories within epics are vertically sliced and sequentially ordered
- No forward dependencies - each story builds only on previous work

---

## Epic 1: Project Foundation & Backend Infrastructure

**Expanded Goal:**

Establish the foundational infrastructure for AutoWeb Outreach AI, including project setup, database architecture, authentication system, and core API framework. This epic delivers a working FastAPI application with PostgreSQL database, JWT authentication, and basic RESTful endpoints that serve as the backbone for all subsequent feature development. Upon completion, the system will have a deployable backend ready to support scraper, evaluator, and generator modules.

**Delivers:** Working FastAPI application with PostgreSQL database, authentication, and basic API endpoints

**Estimated Stories:** 8-10

---

**Story 1.1: Project Initialization and Environment Setup**

As a developer,
I want to initialize the project repository with proper structure and configuration,
So that the team has a consistent development environment and deployment foundation.

**Acceptance Criteria:**
1. Git repository initialized with .gitignore for Python/Node projects
2. Backend directory structure created following FastAPI best practices (app/, models/, routes/, services/)
3. Frontend directory structure created for Next.js 14+ with App Router
4. Docker Compose configuration created for PostgreSQL and Redis services
5. Environment variable management setup (.env.example files for both backend and frontend)
6. README.md created with project overview and setup instructions
7. Basic package.json and requirements.txt created with core dependencies

**Prerequisites:** None (first story)

---

**Story 1.2: PostgreSQL Database Schema and Models**

As a backend developer,
I want to define the database schema and SQLAlchemy models,
So that I can persist business data, evaluations, and templates.

**Acceptance Criteria:**
1. SQLAlchemy Base model configured with database connection settings
2. `businesses` table created with fields: id, name, email, phone, address, website_url, category, description, location, score, created_at, updated_at
3. `evaluations` table created with fields: id, business_id (FK), performance_score, seo_score, accessibility_score, aggregate_score, lighthouse_data (JSONB), evaluated_at
4. `evaluation_problems` table created with fields: id, evaluation_id (FK), problem_type, description, severity
5. `templates` table created with fields: id, business_id (FK), html_content (TEXT), css_content (TEXT), js_content (TEXT), improvements_made (JSONB), variant_number, generated_at
6. Database migrations setup using Alembic
7. Initial migration created and successfully applied to local PostgreSQL instance

**Prerequisites:** Story 1.1 complete

---

**Story 1.3: FastAPI Application Foundation**

As a backend developer,
I want to create the core FastAPI application structure,
So that I can build RESTful API endpoints with proper configuration.

**Acceptance Criteria:**
1. FastAPI app instance created with proper configuration (CORS, middleware)
2. Application factory pattern implemented for testability
3. Environment-based configuration loading (development, production)
4. Database session management with dependency injection
5. Pydantic base settings model created for configuration validation
6. Health check endpoint created: GET /api/health (returns {"status": "healthy"})
7. Application starts successfully and responds to health check
8. CORS configured to allow Next.js frontend origin

**Prerequisites:** Stories 1.1, 1.2 complete

---

**Story 1.4: JWT Authentication System**

As a backend developer,
I want to implement JWT-based authentication,
So that API endpoints can be secured and users can be identified.

**Acceptance Criteria:**
1. User model created with fields: id, email, hashed_password, is_active, created_at
2. Password hashing utility implemented using bcrypt
3. JWT token generation and validation functions created
4. POST /api/auth/register endpoint created (accepts email, password)
5. POST /api/auth/login endpoint created (returns access token)
6. Authentication dependency created for protected routes
7. Token expiration set to 24 hours with refresh token support
8. Successful login returns valid JWT that can be validated

**Prerequisites:** Stories 1.2, 1.3 complete

---

**Story 1.5: Business CRUD API Endpoints**

As a backend developer,
I want to create CRUD endpoints for business management,
So that frontend can interact with business data.

**Acceptance Criteria:**
1. GET /api/businesses endpoint created with pagination (limit, offset)
2. GET /api/businesses/{id} endpoint created returning single business details
3. POST /api/businesses endpoint created (protected, for manual business entry)
4. PUT /api/businesses/{id} endpoint created for updates
5. DELETE /api/businesses/{id} endpoint created (soft delete preferred)
6. Query filtering supported: score range, location, category
7. Pydantic schemas created for request/response validation
8. All endpoints return proper HTTP status codes and error messages
9. Endpoints tested with sample data

**Prerequisites:** Stories 1.3, 1.4 complete

---

**Story 1.6: API Error Handling and Validation**

As a backend developer,
I want comprehensive error handling and validation,
So that API consumers receive clear, actionable error messages.

**Acceptance Criteria:**
1. Custom exception handlers created for common error types (404, 400, 500, 401, 403)
2. Pydantic validation errors return structured, readable error responses
3. Database errors caught and transformed to appropriate HTTP responses
4. Request validation implemented on all endpoints using Pydantic models
5. Error responses follow consistent format: {"error": {"code": "...", "message": "...", "details": {}}}
6. Logging configured to capture errors with appropriate log levels
7. Rate limiting implemented to prevent abuse (100 requests/minute per user)

**Prerequisites:** Story 1.5 complete

---

**Story 1.7: API Documentation with Swagger/OpenAPI**

As a frontend developer,
I want auto-generated API documentation,
So that I can understand available endpoints and their schemas.

**Acceptance Criteria:**
1. FastAPI automatic OpenAPI schema generation enabled
2. Swagger UI accessible at /docs endpoint
3. ReDoc documentation accessible at /redoc endpoint
4. All endpoints documented with descriptions and example requests/responses
5. Pydantic schemas provide clear field descriptions and types
6. Authentication requirements clearly indicated in documentation
7. Example values provided for all request bodies

**Prerequisites:** Story 1.5 complete

---

**Story 1.8: Database Indexing and Performance Optimization**

As a backend developer,
I want to optimize database queries with proper indexing,
So that API responses remain fast as data volume grows.

**Acceptance Criteria:**
1. Index created on businesses.score for filtering
2. Index created on businesses.location for geographic queries
3. Index created on businesses.category for niche filtering
4. Index created on businesses.created_at for sorting
5. Composite index created on (score, location) for common filter combinations
6. Foreign key indexes verified on all relationship columns
7. Query performance tested with 1000+ business records, all queries < 100ms

**Prerequisites:** Story 1.2 complete

---

**Story 1.9: Backend Testing Framework Setup**

As a backend developer,
I want a testing framework configured,
So that I can write and run automated tests for API endpoints.

**Acceptance Criteria:**
1. Pytest configured with FastAPI test client
2. Test database setup with automatic cleanup between tests
3. Factory fixtures created for generating test data (businesses, users)
4. Sample tests written for authentication endpoints (login, register)
5. Sample tests written for business CRUD endpoints
6. Test coverage reporting configured
7. All tests pass successfully
8. GitHub Actions or CI pipeline configured to run tests on push

**Prerequisites:** Stories 1.4, 1.5 complete

---

**Story 1.10: Deployment Configuration and Documentation**

As a DevOps engineer,
I want deployment configuration and documentation,
So that the application can be deployed to production environment.

**Acceptance Criteria:**
1. Dockerfile created for FastAPI backend with multi-stage build
2. Docker Compose production configuration created
3. Environment variable documentation complete with all required settings
4. Database migration instructions documented
5. Deployment guide created covering: environment setup, database initialization, application startup
6. Health check endpoint verified for container orchestration
7. Application successfully runs in Docker container locally

**Prerequisites:** Stories 1.3, 1.8 complete

---

## Epic 2: Business Discovery & Scraper Module

**Expanded Goal:**

Build an automated web scraping system that discovers UK businesses from directories (Checkatrade, Yell), extracts comprehensive business data, and stores it in the database with proper validation and deduplication. This epic delivers a fully functional scraper that can be configured with geographic and niche filters, handles rate limiting gracefully, and provides progress tracking for long-running operations.

**Delivers:** Functional scraper discovering businesses from Checkatrade/Yell with filtering, validation, and storage

**Estimated Stories:** 7-9

---

**Story 2.1: Scraping Job Model and API Endpoints**

As a backend developer,
I want to create scraping job management functionality,
So that users can initiate and track scraping operations.

**Acceptance Criteria:**
1. `scraping_jobs` table created with fields: id, user_id (FK), status, location_filter, category_filter, total_found, total_processed, started_at, completed_at, error_message
2. ScrapingJob SQLAlchemy model created with relationships
3. POST /api/scraping-jobs endpoint created to initiate new job
4. GET /api/scraping-jobs/{id} endpoint created to check job status
5. GET /api/scraping-jobs endpoint created to list user's jobs with pagination
6. Job status enum: pending, running, completed, failed
7. Pydantic schemas created for request/response validation

**Prerequisites:** Epic 1 complete

---

**Story 2.2: Selenium WebDriver Setup and Configuration**

As a backend developer,
I want Selenium WebDriver configured for web scraping,
So that I can programmatically navigate and extract data from directory websites.

**Acceptance Criteria:**
1. Selenium WebDriver installed and configured (headless Chrome)
2. WebDriver manager setup for automatic driver version management
3. Browser configuration includes: headless mode, user agent rotation, window size
4. WebDriver instance creation utility function with proper error handling
5. Resource cleanup (driver.quit()) handled properly with context managers
6. Connection timeout and page load timeout configured (30 seconds)
7. Test script successfully opens Checkatrade.com homepage and extracts title

**Prerequisites:** Epic 1 complete

---

**Story 2.3: Checkatrade Scraper Implementation**

As a backend developer,
I want to scrape business data from Checkatrade,
So that I can discover UK businesses with their contact information.

**Acceptance Criteria:**
1. Checkatrade search URL builder created accepting location and category parameters
2. Business listing page parser extracts individual business URLs
3. Business detail page parser extracts: name, phone, email, address, website URL, category, description
4. Pagination handling implemented to traverse multiple result pages
5. Rate limiting implemented: 2-second delay between requests
6. Data extraction tested successfully on 10+ real Checkatrade listings
7. Extracted data validated against expected schema before storage

**Prerequisites:** Story 2.2 complete

---

**Story 2.4: Yell Scraper Implementation**

As a backend developer,
I want to scrape business data from Yell.com,
So that I can discover additional UK businesses beyond Checkatrade.

**Acceptance Criteria:**
1. Yell.com search URL builder created accepting location and category parameters
2. Business listing page parser extracts individual business URLs
3. Business detail page parser extracts: name, phone, email, address, website URL, category, description
4. Pagination handling implemented to traverse result pages
5. Rate limiting implemented: 2-second delay between requests
6. Data extraction tested successfully on 10+ real Yell listings
7. Extracted data validated and normalized to match Checkatrade format

**Prerequisites:** Story 2.2 complete

---

**Story 2.5: Data Validation and Deduplication**

As a backend developer,
I want to validate and deduplicate scraped business data,
So that the database contains only high-quality, unique business records.

**Acceptance Criteria:**
1. Business data validator checks required fields: name, website_url at minimum
2. Email validation using regex pattern
3. Phone number normalization (UK format: +44...)
4. Website URL validation and normalization (ensure https://, remove trailing slashes)
5. Duplicate detection based on website URL (case-insensitive)
6. Duplicate detection based on exact name + address match
7. Invalid records logged but don't stop scraping process
8. Duplicate businesses update existing record if new data is more complete

**Prerequisites:** Story 2.1 complete

---

**Story 2.6: Background Job Processing with Celery**

As a backend developer,
I want scraping jobs to run asynchronously in background,
So that API requests don't timeout and users can track progress.

**Acceptance Criteria:**
1. Celery configured with Redis as message broker
2. Celery worker setup with proper task configuration
3. Scraping task implemented as Celery task accepting job_id parameter
4. Task updates scraping_job record with progress (total_found, total_processed)
5. Task handles exceptions and updates job status to "failed" with error message
6. Task completion updates job status to "completed" with final counts
7. Celery worker starts successfully and processes test task
8. POST /api/scraping-jobs endpoint returns immediately while task runs in background

**Prerequisites:** Stories 2.1, 2.3 complete

---

**Story 2.7: Scraping Progress Tracking and Notifications**

As a user,
I want to see real-time progress of my scraping job,
So that I know when it's complete and how many businesses were found.

**Acceptance Criteria:**
1. ScrapingJob model includes progress fields: businesses_found, businesses_processed, current_page
2. Scraping task updates progress every 10 businesses processed
3. GET /api/scraping-jobs/{id} returns current progress in response
4. Frontend polling mechanism can check progress every 5 seconds
5. Job completion triggers final status update
6. Error scenarios update job with error_message and failed status
7. Progress tracking tested with scraping job finding 50+ businesses

**Prerequisites:** Story 2.6 complete

---

**Story 2.8: Scraper Error Handling and Retry Logic**

As a backend developer,
I want robust error handling in the scraper,
So that temporary failures don't stop the entire scraping process.

**Acceptance Criteria:**
1. Network errors (timeout, connection refused) trigger retry with exponential backoff (max 3 retries)
2. Missing elements on page logged as warnings, business skipped gracefully
3. Invalid HTML structure handled without crashing scraper
4. Rate limit detection (429 responses) triggers longer delay before retry
5. Scraper continues to next business if one business fails to parse
6. All errors logged with context (URL, business name if available, error details)
7. Final job summary includes: total_attempted, total_successful, total_failed

**Prerequisites:** Story 2.6 complete

---

**Story 2.9: Geographic and Niche Filtering**

As a user,
I want to filter scraping by location and business category,
So that I only discover businesses relevant to my target market.

**Acceptance Criteria:**
1. Location filter accepts: postcode, city name, or region
2. Category filter accepts: directory-specific categories (e.g., "Plumbing", "Electrician")
3. POST /api/scraping-jobs request validation ensures at least one filter provided
4. Scraper builds search URLs with filter parameters for each directory
5. Filters applied correctly result in only matching businesses being scraped
6. Multiple category selection supported (OR logic: Plumbing OR Heating)
7. Geographic radius filter supported (e.g., within 10 miles of postcode)

**Prerequisites:** Stories 2.3, 2.4 complete

---

## Epic 3: Website Evaluation & Scoring System

**Expanded Goal:**

Integrate Google Lighthouse CLI to automatically evaluate discovered websites, calculate aggregate quality scores, and identify specific performance/SEO/accessibility problems. This epic delivers a reliable evaluation engine that processes businesses in the background, generates objective scores on a 0-100 scale, and flags businesses scoring below 70% for template generation.

**Delivers:** Automated website evaluation with Lighthouse scoring and problem identification

**Estimated Stories:** 6-8

---

**Story 3.1: Lighthouse CLI Integration and Setup**

As a backend developer,
I want to integrate Google Lighthouse CLI,
So that I can programmatically evaluate website quality.

**Acceptance Criteria:**
1. Lighthouse npm package installed globally in backend container
2. Python subprocess wrapper created to execute Lighthouse CLI commands
3. Lighthouse configuration created: desktop mode, mobile emulation, standard throttling
4. Lighthouse output format set to JSON for parsing
5. Timeout configured for Lighthouse execution (60 seconds per site)
6. Test evaluation successfully runs on sample website and returns JSON report
7. Lighthouse metrics extracted: performance score, SEO score, accessibility score, best-practices score

**Prerequisites:** Epic 1 complete

---

**Story 3.2: Evaluation Service and Score Calculation**

As a backend developer,
I want to create an evaluation service that calculates aggregate scores,
So that businesses can be ranked and compared objectively.

**Acceptance Criteria:**
1. EvaluationService class created with method: evaluate_website(business_id)
2. Lighthouse report parser extracts individual category scores (0-1 scale)
3. Aggregate score calculated as weighted average: Performance (40%), SEO (30%), Accessibility (20%), Best Practices (10%)
4. Aggregate score converted to 0-100 scale for user-friendly display
5. Evaluation results saved to evaluations table with lighthouse_data JSONB field containing full report
6. Business record updated with calculated aggregate score
7. Service tested successfully evaluating 5+ different websites

**Prerequisites:** Story 3.1 complete

---

**Story 3.3: Problem Identification and Categorization**

As a backend developer,
I want to extract specific problems from Lighthouse audits,
So that users understand exactly what's wrong with each website.

**Acceptance Criteria:**
1. Lighthouse audit parser identifies failed audits from report
2. Problems categorized by type: performance, seo, accessibility, best-practices
3. Severity assigned based on audit impact: critical (score impact >10 points), major (5-10 points), minor (<5 points)
4. Problem descriptions extracted from audit details
5. Problems saved to evaluation_problems table linked to evaluation
6. Maximum 10 most impactful problems stored per evaluation
7. Problems retrievable via GET /api/evaluations/{id}/problems endpoint

**Prerequisites:** Story 3.2 complete

---

**Story 3.4: Automatic Evaluation Trigger After Scraping**

As a backend developer,
I want evaluations to automatically trigger after businesses are scraped,
So that scores are available without manual intervention.

**Acceptance Criteria:**
1. Scraping task triggers evaluation task after each business is saved
2. Evaluation task queued as Celery task to run asynchronously
3. Business record updated with evaluation_status: pending, evaluating, completed, failed
4. Failed evaluations logged with error message but don't block other evaluations
5. Scraping job continues independently of evaluation progress
6. Evaluation tasks prioritized in Celery queue (high priority)
7. System tested successfully scraping and evaluating 20+ businesses end-to-end

**Prerequisites:** Stories 2.6, 3.2 complete

---

**Story 3.5: Score-Based Business Flagging for Template Generation**

As a backend developer,
I want businesses with scores below 70% automatically flagged,
So that the template generation system knows which businesses to process.

**Acceptance Criteria:**
1. Business model includes template_generation_status field: not_needed (score >=70), pending, generating, completed, failed
2. After evaluation completes, check if aggregate_score < 70
3. If score < 70, update template_generation_status to "pending"
4. If score >= 70, update template_generation_status to "not_needed"
5. GET /api/businesses endpoint supports filtering by template_generation_status
6. Business cards in frontend show different indicators based on status
7. System correctly flags businesses in test dataset

**Prerequisites:** Story 3.2 complete

---

**Story 3.6: Evaluation API Endpoints**

As a frontend developer,
I want API endpoints to access evaluation data,
So that I can display scores and problems in the UI.

**Acceptance Criteria:**
1. GET /api/businesses/{id}/evaluation endpoint returns latest evaluation for business
2. GET /api/evaluations/{id} endpoint returns full evaluation details
3. GET /api/evaluations/{id}/problems endpoint returns categorized problem list
4. Response includes: all individual scores, aggregate score, evaluation timestamp, problem count
5. POST /api/evaluations endpoint created to manually trigger re-evaluation
6. Endpoints return proper 404 if business has no evaluation yet
7. All endpoints tested and returning expected data format

**Prerequisites:** Story 3.3 complete

---

**Story 3.7: Lighthouse Error Handling and Fallback Scoring**

As a backend developer,
I want graceful handling of Lighthouse failures,
So that evaluation continues even when some sites can't be analyzed.

**Acceptance Criteria:**
1. Timeout errors (site doesn't load in 60 seconds) handled gracefully
2. Sites requiring authentication marked as "evaluation_failed" with reason
3. Sites with invalid SSL certificates handled without crashing
4. Sites with heavy JavaScript that don't render marked with warning
5. Fallback heuristic scoring implemented for failed Lighthouse evaluations (basic HTTP response analysis)
6. Failed evaluations still save to database with failure_reason field
7. Evaluation success rate tracked in scraping job statistics

**Prerequisites:** Story 3.2 complete

---

**Story 3.8: Evaluation Performance Optimization**

As a backend developer,
I want evaluations to run efficiently at scale,
So that hundreds of businesses can be evaluated in reasonable time.

**Acceptance Criteria:**
1. Celery worker pool configured with 4 concurrent evaluation workers
2. Lighthouse runs in headless mode with minimal overhead
3. Parallel evaluation of multiple businesses (up to 4 concurrent)
4. Evaluation results cached in Redis with 24-hour TTL
5. Re-evaluation only triggered if business website_url changed
6. Evaluation queue prioritizes businesses without scores
7. Performance tested: 100 businesses evaluated in under 2 hours

**Prerequisites:** Stories 3.4, 3.7 complete

---

## Epic 4: AI Template Generation Engine

**Expanded Goal:**

Integrate OpenAI GPT-4 API to automatically generate personalized, professional website templates for businesses scoring below 70%. This epic delivers an AI-powered generation system that injects business-specific data into prompts, generates 2-3 design variants per business, stores complete HTML/CSS/JS templates in the database, and tracks improvements made in each generated template.

**Delivers:** AI template generation producing personalized website designs for qualifying businesses

**Estimated Stories:** 7-9

---

**Story 4.1: OpenAI API Integration and Configuration**

As a backend developer,
I want to integrate OpenAI GPT-4 API,
So that I can programmatically generate website templates.

**Acceptance Criteria:**
1. OpenAI Python SDK installed and configured
2. API key management through environment variables
3. OpenAI client initialization with error handling
4. API rate limiting configured (RPM tracking)
5. Token usage tracking for cost monitoring
6. Test API call successfully completes and returns response
7. Error handling for API failures (rate limits, invalid responses, timeouts)

**Prerequisites:** Epic 1 complete

---

**Story 4.2: Template Generation Prompt Engineering**

As a backend developer,
I want optimized prompts for website template generation,
So that GPT-4 produces high-quality, production-ready HTML templates.

**Acceptance Criteria:**
1. Base prompt template created including: business data placeholders, design requirements, technical constraints
2. Prompt includes explicit instructions: mobile-first responsive, modern design, SEO-optimized, performance-optimized
3. Prompt specifies output format: complete HTML document with inline CSS and minimal JavaScript
4. Prompt incorporates business problems identified during evaluation
5. System message configured to set GPT-4 role as "expert web designer"
6. Temperature set to 0.7 for creative but consistent outputs
7. Test generation produces valid, well-structured HTML template

**Prerequisites:** Story 4.1 complete

---

**Story 4.3: Business Data Injection and Prompt Building**

As a backend developer,
I want to dynamically build prompts with business-specific data,
So that each template is personalized for the target business.

**Acceptance Criteria:**
1. PromptBuilder class created with method: build_template_prompt(business_id)
2. Business data extracted: name, category, description, phone, email, address, website_url
3. Evaluation problems extracted and formatted for prompt context
4. Industry-specific design guidelines selected based on business category
5. Prompt variables safely escaped to prevent injection issues
6. Final prompt length validated (within GPT-4 token limits: ~8000 tokens)
7. Test prompts generated for 5+ different business types

**Prerequisites:** Stories 3.3, 4.2 complete

---

**Story 4.4: Template Generation Service**

As a backend developer,
I want a service that orchestrates template generation,
So that templates are created reliably and stored correctly.

**Acceptance Criteria:**
1. TemplateGenerationService class created with method: generate_templates(business_id, variant_count=3)
2. Service calls OpenAI API for each variant with slightly different prompts
3. Generated HTML validated for basic structure (DOCTYPE, html, head, body tags)
4. CSS extracted from generated HTML (if separate or inline)
5. JavaScript extracted from generated HTML (if separate or inline)
6. Template saved to templates table with variant_number (1, 2, 3)
7. improvements_made field populated with list of problems addressed
8. Business template_generation_status updated to "completed"

**Prerequisites:** Stories 4.2, 4.3 complete

---

**Story 4.5: Automatic Template Generation Trigger**

As a backend developer,
I want template generation to automatically trigger for qualifying businesses,
So that previews are available without manual intervention.

**Acceptance Criteria:**
1. After evaluation completes and business is flagged (score < 70), generation task queued
2. Generation runs as Celery task to avoid blocking
3. Task updates business template_generation_status: pending → generating → completed/failed
4. Failed generations logged with error details and retry attempted once
5. Generation only triggers once per business (check template_generation_status)
6. System tested with evaluation→generation pipeline for 10+ businesses
7. Generated templates successfully saved and retrievable

**Prerequisites:** Stories 3.5, 4.4 complete

---

**Story 4.6: Template API Endpoints**

As a frontend developer,
I want API endpoints to access generated templates,
So that I can display them in the preview interface.

**Acceptance Criteria:**
1. GET /api/businesses/{id}/templates endpoint returns all template variants
2. GET /api/templates/{id} endpoint returns specific template details
3. GET /api/templates/{id}/preview endpoint returns rendered HTML for preview
4. Response includes: variant_number, improvements_made, generated_at, preview URLs
5. POST /api/businesses/{id}/regenerate-templates endpoint triggers new generation
6. Endpoints return proper 404 if no templates exist
7. Large HTML content returned efficiently (compression enabled)

**Prerequisites:** Story 4.4 complete

---

**Story 4.7: Template Quality Validation**

As a backend developer,
I want to validate generated template quality,
So that only professional-looking templates are shown to users.

**Acceptance Criteria:**
1. HTML validator checks for valid HTML5 structure
2. Responsive meta viewport tag presence validated
3. Business data injection verified (name, phone, email appear in generated HTML)
4. Minimum content length check (> 1000 characters HTML)
5. No placeholder text check (no "Lorem ipsum", "[Business Name]", etc.)
6. CSS validation checks for mobile-responsive media queries
7. Failed validations trigger automatic regeneration (max 2 attempts)

**Prerequisites:** Story 4.4 complete

---

**Story 4.8: Template Improvements Tracking**

As a user,
I want to see what improvements each template provides,
So that I can explain the value to prospects.

**Acceptance Criteria:**
1. TemplateAnalyzer class compares old site problems with new template features
2. Improvements categorized: performance (fast loading), SEO (meta tags), mobile (responsive), accessibility
3. improvements_made JSONB field populated with structured improvement list
4. Each improvement includes: category, description, impact (high/medium/low)
5. GET /api/templates/{id}/improvements endpoint returns formatted improvement list
6. Improvements displayed in frontend preview panel
7. Test templates show relevant, accurate improvements based on original problems

**Prerequisites:** Stories 3.3, 4.4 complete

---

**Story 4.9: Generation Cost Tracking and Optimization**

As a product owner,
I want to track and optimize AI generation costs,
So that the platform remains economically viable at scale.

**Acceptance Criteria:**
1. Token usage logged for each generation request (prompt tokens + completion tokens)
2. Cost calculated based on GPT-4 pricing (per 1K tokens)
3. Generation cost saved in template record
4. Monthly cost tracking dashboard endpoint: GET /api/analytics/generation-costs
5. Prompt optimization reduces average token usage by 20% vs baseline
6. Caching implemented: same business regeneration uses cached variant as base
7. Cost per template tracked: target < £0.50 per business (3 variants)

**Prerequisites:** Stories 4.1, 4.4 complete

## Epic 5: Frontend Business Cards & Discovery UI

**Expanded Goal:**

Build the Next.js 14+ frontend application with business card grid, real-time search, multi-dimensional filtering, and detail views. This epic delivers a professional, animated web interface that allows users to browse discovered leads, filter by score/location/category, search across all data fields, and view comprehensive business details with evaluation results.

**Delivers:** Professional web interface for lead browsing with search, filtering, and animated business cards

**Estimated Stories:** 8-10

---

**Story 5.1: Next.js Application Foundation**

As a frontend developer,
I want to initialize Next.js 14+ application with proper configuration,
So that I have a modern frontend framework ready for feature development.

**Acceptance Criteria:**
1. Next.js 14+ initialized with App Router architecture
2. TypeScript configured with strict mode enabled
3. Tailwind CSS installed and configured with custom design system colors
4. Framer Motion installed for animations
5. API client configured to connect to FastAPI backend (axios or fetch)
6. Environment variables setup for API URL configuration
7. Application starts successfully and renders homepage
8. ESLint and Prettier configured for code quality

**Prerequisites:** Epic 1 complete (backend API available)

---

**Story 5.2: Authentication UI and Protected Routes**

As a frontend developer,
I want user authentication flows implemented,
So that users can register, login, and access protected pages.

**Acceptance Criteria:**
1. Login page created at /login with form (email, password)
2. Register page created at /register with form (email, password, confirm password)
3. JWT token stored securely in httpOnly cookies or localStorage
4. API client includes JWT token in Authorization header
5. Protected route wrapper redirects unauthenticated users to /login
6. Logout functionality clears token and redirects to login
7. Form validation provides clear error messages
8. Successful login redirects to dashboard

**Prerequisites:** Story 5.1 complete, Epic 1 Story 1.4 (backend auth) complete

---

**Story 5.3: Dashboard Layout and Navigation**

As a user,
I want a clean dashboard layout with navigation,
So that I can easily access different sections of the platform.

**Acceptance Criteria:**
1. Dashboard layout created with sidebar navigation
2. Navigation links: Dashboard, Businesses, Scraping Jobs
3. Header includes user info and logout button
4. Responsive layout works on desktop, tablet, and mobile
5. Active navigation state highlighted
6. Smooth page transitions using Framer Motion
7. Dashboard home page shows quick stats (total businesses, qualified leads, templates generated)
8. Stats data fetched from backend API endpoints

**Prerequisites:** Story 5.2 complete

---

**Story 5.4: Business Card Component**

As a frontend developer,
I want a reusable business card component,
So that I can display business information consistently.

**Acceptance Criteria:**
1. BusinessCard component created accepting business data as props
2. Card displays: business name, category, description
3. Contact info displayed: email (with mailto link), phone (with tel link), address
4. Website URL displayed as clickable link (opens in new tab)
5. Score badge displayed with color coding: red if score < 70, green if >= 70
6. Problem indicators shown as icons (performance, SEO, accessibility) with tooltips
7. Card has hover state with subtle elevation animation
8. Click on card navigates to business detail view
9. Component responsive and works on mobile devices

**Prerequisites:** Story 5.1 complete

---

**Story 5.5: Business Card Grid with Pagination**

As a user,
I want to browse businesses in a responsive grid layout,
So that I can efficiently review discovered leads.

**Acceptance Criteria:**
1. Grid layout created displaying business cards (4 columns desktop, 2 tablet, 1 mobile)
2. Data fetched from GET /api/businesses endpoint with pagination
3. Pagination controls display at bottom (Previous, Page numbers, Next)
4. Loading skeleton shown while data fetches
5. Empty state message displayed when no businesses found
6. Staggered card entry animation using Framer Motion
7. Grid re-renders smoothly when filters applied
8. Performance optimized for 100+ businesses (virtualization if needed)

**Prerequisites:** Story 5.4 complete

---

**Story 5.6: Real-Time Search Functionality**

As a user,
I want to search across all business data fields,
So that I can quickly find specific businesses.

**Acceptance Criteria:**
1. Search input field added above business card grid
2. Search triggers on input change with 300ms debounce
3. Search filters businesses client-side for immediate feedback
4. Search matches: business name, category, location, email, phone
5. Search is case-insensitive
6. Search results update grid in real-time
7. Clear search button (X icon) resets filter
8. Search placeholder text provides usage hints
9. Grid shows "No results found" message when search returns empty

**Prerequisites:** Story 5.5 complete

---

**Story 5.7: Multi-Dimensional Filter System**

As a user,
I want to filter businesses by multiple criteria,
So that I can focus on specific segments of leads.

**Acceptance Criteria:**
1. Filter sidebar created with collapsible sections
2. Score range filter: slider or buttons for <70, 70-85, >85
3. Location filter: dropdown or autocomplete for cities/regions
4. Category filter: checkboxes for business types
5. Problem type filter: checkboxes for performance, SEO, accessibility issues
6. Template status filter: buttons for pending, completed, not needed
7. Multiple filters combine with AND logic
8. Active filters displayed as removable chips
9. "Clear all filters" button resets to default state
10. Filter state persists in URL query parameters
11. Grid updates immediately when filters change

**Prerequisites:** Story 5.5 complete

---

**Story 5.8: Business Detail View**

As a user,
I want to view comprehensive details for a specific business,
So that I can make informed outreach decisions.

**Acceptance Criteria:**
1. Detail page created at /businesses/[id]
2. Page displays all business information: name, category, description, contact details
3. Website URL shown with "Visit Website" button (opens in new tab)
4. Score breakdown visualization (circular progress bars for each category)
5. Detailed problem list displayed with categorization and severity
6. Evaluation timestamp shown
7. Template generation status indicator displayed
8. "Preview Templates" button shown if templates available
9. "Re-evaluate Website" button triggers new evaluation
10. Loading state while data fetches
11. Error handling for invalid business ID (404 page)

**Prerequisites:** Story 5.4 complete

---

**Story 5.9: Scraping Job Management UI**

As a user,
I want to initiate and track scraping jobs,
So that I can discover new businesses on demand.

**Acceptance Criteria:**
1. "New Scraping Job" page created with form
2. Form fields: location (text input), category (dropdown with common categories)
3. Form validation ensures required fields filled
4. Submit triggers POST /api/scraping-jobs and redirects to job status page
5. Job status page shows: progress bar, businesses found count, current status
6. Status page polls GET /api/scraping-jobs/{id} every 5 seconds for updates
7. Completion message shown when job finishes
8. "View Results" button navigates to business grid filtered to new businesses
9. Job list page shows all previous jobs with status and results count

**Prerequisites:** Story 5.3 complete, Epic 2 complete (backend scraping)

---

**Story 5.10: Animations and Polish**

As a user,
I want smooth animations and polished interactions,
So that the platform feels professional and premium.

**Acceptance Criteria:**
1. Page transitions animated using Framer Motion (fade + slide)
2. Card hover animations: subtle lift and shadow increase
3. Score badge numbers animate on mount (count up effect)
4. Filter panel slide-in animation when opened
5. Search results fade in/out smoothly
6. Button interactions have hover/active states
7. Loading spinners use branded animations
8. Toast notifications for actions (evaluation triggered, export completed)
9. Micro-interactions on icon buttons (scale on click)
10. Animations respect prefers-reduced-motion for accessibility

**Prerequisites:** Stories 5.4, 5.5, 5.7 complete

---

## Epic 6: Template Preview & Comparison System

**Expanded Goal:**

Create the template preview interface that renders AI-generated HTML templates, enables navigation between design variants, provides side-by-side comparison with old website, includes mobile/desktop toggle, and highlights improvements made. This epic delivers the complete "wow" moment showing prospects their transformed website.

**Delivers:** Complete template preview experience with live rendering and comparison

**Estimated Stories:** 6-8

---

**Story 6.1: Template Preview Modal Component**

As a frontend developer,
I want a full-screen preview modal,
So that users can view templates without distraction.

**Acceptance Criteria:**
1. Modal component created covering entire viewport
2. Modal triggered from "Preview Templates" button on business card or detail page
3. Close button (X) in top-right corner dismisses modal
4. ESC key closes modal
5. Click outside modal content closes modal
6. Modal has smooth enter/exit animation (fade + scale)
7. Modal prevents body scroll when open
8. Z-index ensures modal appears above all other content

**Prerequisites:** Story 5.4 complete

---

**Story 6.2: Template Variant Selector**

As a user,
I want to switch between template design variants,
So that I can evaluate different options for the same business.

**Acceptance Criteria:**
1. Variant selector displayed as tabs or segmented control (Design 1, 2, 3)
2. Active variant highlighted visually
3. Click on variant tab loads that template immediately
4. Smooth transition animation when switching variants
5. Variant data fetched from GET /api/businesses/{id}/templates
6. Loading state shown while template fetches
7. If only 1-2 variants available, selector adapts appropriately
8. Keyboard navigation supported (arrow keys to switch variants)

**Prerequisites:** Story 6.1 complete, Epic 4 complete (templates generated)

---

**Story 6.3: Live HTML Template Rendering**

As a user,
I want to see the generated template rendered live,
So that I can evaluate the actual design and layout.

**Acceptance Criteria:**
1. Template HTML rendered in sandboxed iframe for security
2. Iframe sized to show full template (scrollable if needed)
3. Template HTML fetched from GET /api/templates/{id}/preview endpoint
4. CSS and JavaScript from template properly executed in iframe
5. Iframe sandbox permissions configured (allow-scripts, allow-same-origin)
6. Loading spinner shown while iframe content loads
7. Error handling if template fails to render
8. External resource loading (fonts, images) works correctly in iframe

**Prerequisites:** Story 6.2 complete

---

**Story 6.4: Mobile/Desktop Preview Toggle**

As a user,
I want to toggle between mobile and desktop previews,
So that I can verify responsive behavior.

**Acceptance Criteria:**
1. Toggle control displayed (icons or buttons: Desktop / Mobile)
2. Desktop mode: iframe full width (up to 1440px)
3. Mobile mode: iframe constrained to 375px width with device frame
4. Smooth transition animation when toggling
5. Mobile preview shows device chrome (iPhone or generic smartphone frame)
6. Toggle state persists when switching variants
7. Default mode is desktop
8. Responsive toggle works on actual mobile devices (shows preview smaller)

**Prerequisites:** Story 6.3 complete

---

**Story 6.5: Side-by-Side Comparison View**

As a user,
I want to see old website vs new template side-by-side,
So that I can clearly visualize the improvement.

**Acceptance Criteria:**
1. Comparison mode activated via toggle or button
2. Split-screen layout: left side shows old website, right side shows new template
3. Both sides rendered in iframes
4. Synchronized scrolling (optional: scroll one side, other follows)
5. Divider between sides draggable to adjust width ratio
6. Labels clearly indicate "Current Website" vs "New Design"
7. Smooth transition entering/exiting comparison mode
8. Comparison mode works with mobile/desktop toggle

**Prerequisites:** Story 6.3 complete

---

**Story 6.6: Improvements Panel**

As a user,
I want to see a list of improvements the template provides,
So that I can understand the value proposition for prospects.

**Acceptance Criteria:**
1. Improvements panel displayed in modal sidebar or below preview
2. Data fetched from GET /api/templates/{id}/improvements endpoint
3. Improvements categorized by type: Performance, SEO, Mobile, Accessibility
4. Each improvement shows: icon, category, description, impact level
5. Impact level color-coded: High (green), Medium (yellow), Low (gray)
6. Panel collapsible to maximize preview space
7. Panel updates when switching template variants
8. "Copy improvements" button copies formatted list to clipboard
9. Panel responsive on mobile devices

**Prerequisites:** Story 6.3 complete, Epic 4 Story 4.8 (improvements tracking) complete

---

**Story 6.7: Preview Sharing and Export**

As a user,
I want to share template previews,
So that I can send them to prospects or save for later.

**Acceptance Criteria:**
1. "Share Preview" button generates shareable link
2. Shareable link works without authentication (public preview)
3. Public preview page displays template with business name
4. "Export HTML" button downloads template as .html file
5. "Screenshot" button captures preview as PNG image
6. Copy link button copies shareable URL to clipboard
7. Toast notification confirms successful copy/export
8. Shared preview includes branding: "Generated by AutoWeb Outreach AI"

**Prerequisites:** Story 6.3 complete

---

**Story 6.8: Preview Performance Optimization**

As a frontend developer,
I want preview rendering optimized for performance,
So that large templates load quickly.

**Acceptance Criteria:**
1. Template HTML cached in browser after first load
2. Iframe loading uses loading="lazy" where appropriate
3. Large template HTML (>500KB) compressed before transmission
4. Preview preloads next/previous variants for instant switching
5. Debounce rapid variant switching to prevent unnecessary renders
6. Service worker caches template assets for offline viewing
7. Performance tested: template previews load in < 3 seconds on 4G connection

**Prerequisites:** Stories 6.2, 6.3 complete

---

## Summary

**Total Stories:** 54 stories across 6 epics

**Epic Breakdown:**
- Epic 1: Project Foundation & Backend Infrastructure (10 stories)
- Epic 2: Business Discovery & Scraper Module (9 stories)
- Epic 3: Website Evaluation & Scoring System (8 stories)
- Epic 4: AI Template Generation Engine (9 stories)
- Epic 5: Frontend Business Cards & Discovery UI (10 stories)
- Epic 6: Template Preview & Comparison System (8 stories)

**Delivery Sequence:**
1. Complete Epic 1 to establish foundation
2. Build backend data pipeline: Epics 2 → 3 → 4
3. Develop frontend interfaces: Epics 5 → 6
4. Integration testing and polish

**Estimated Timeline:** 8-12 weeks for MVP completion (Level 3 project)

---

## Story Guidelines Reference

**Story Format:**

```
**Story [EPIC.N]: [Story Title]**

As a [user type],
I want [goal/desire],
So that [benefit/value].

**Acceptance Criteria:**
1. [Specific testable criterion]
2. [Another specific criterion]
3. [etc.]

**Prerequisites:** [Dependencies on previous stories, if any]
```

**Story Requirements:**

- **Vertical slices** - Complete, testable functionality delivery
- **Sequential ordering** - Logical progression within epic
- **No forward dependencies** - Only depend on previous work
- **AI-agent sized** - Completable in 2-4 hour focused session
- **Value-focused** - Integrate technical enablers into value-delivering stories

---

**For implementation:** Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown.
