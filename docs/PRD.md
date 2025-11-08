# AutoWeb_Outreach_AI Product Requirements Document (PRD)

**Author:** azeem yaqoob
**Date:** 2025-10-31
**Project Level:** 3
**Target Scale:** Medium-scale web platform (15-40 stories)

---

## Goals and Background Context

### Goals

- **Transform Lead Generation**: Convert manual, time-intensive lead research (10+ hours per 50 prospects) into automated, AI-powered discovery completing in under 1 hour
- **Drive Client Acquisition**: Generate 5-10 new web development clients within first 6 months of platform launch
- **Build Prospect Database**: Create qualified lead database of 500+ UK businesses with websites scoring below 70% on performance metrics
- **Scale AI Preview Generation**: Automatically generate 200+ personalized website template previews demonstrating transformation potential
- **Achieve Operational Efficiency**: Realize 80% time savings vs. manual lead generation process
- **Increase Outreach Effectiveness**: Improve email response rates from 2-5% (industry baseline) to 15%+ through visual proof-of-concept
- **Validate Business Model**: Achieve break-even within 3-5 client conversions, demonstrating platform ROI
- **Enable Scalable Outreach**: Support 100+ qualified leads per week by Month 6 without proportional resource increase

### Background Context

**The Market Opportunity**

Hundreds of thousands of UK small-to-medium businesses operate websites that actively harm their competitiveness. These sites suffer from slow loading times (>3 seconds), poor SEO rankings, non-responsive mobile designs, and outdated visual presentation. An estimated 300,000+ UK SMBs have websites scoring below 70% on standard performance metrics, representing massive untapped market opportunity.

**The Core Problem**

Despite clear website deficiencies, these businesses rarely seek redesign services proactively. They lack three critical elements: (1) concrete metrics showing exactly what's broken, (2) visual proof of what a modern alternative could deliver, and (3) confidence that redesign investment will generate measurable ROI. This creates a paradox where businesses needing websites most urgently are least likely to pursue solutions.

**Current State Challenges**

Web development agencies face expensive, low-conversion cold outreach (2-5% response rates). Manual lead research consumes 2-5 hours per prospect. Creating personalized demos or mockups for each prospect is prohibitively time-intensive. Generic pitches ("we can improve your website") fail to differentiate or demonstrate tangible value, resulting in poor conversion rates and high customer acquisition costs.

**The Innovation**

AutoWeb Outreach AI addresses this gap through intelligent automation and AI-powered personalization at scale. By combining automated prospect discovery, objective Lighthouse-based evaluation, and GPT-4 generated website previews personalized with actual business data, the platform creates "show, don't tell" sales collateral automatically. Each prospect receives a stunning visual demonstration of their transformed website, making the value proposition immediately tangible and dramatically increasing response rates.

**Strategic Value**

This platform transforms lead generation from a manual bottleneck into an automated competitive advantage, enabling web development agencies to scale client acquisition without proportionally scaling effort or cost.

---

## Requirements

### Functional Requirements

**Scraper Module**

- **FR001**: System shall scrape UK business directories (Checkatrade, Yell) to extract business data including name, email, phone, address, website URL, category, and description
- **FR002**: System shall support geographic filtering by postcode and city to target specific regions
- **FR003**: System shall support niche/category filtering to focus on specific business types
- **FR004**: System shall validate and deduplicate scraped data before storage to prevent duplicate entries
- **FR005**: System shall implement rate limiting and error handling to respect directory servers and handle failures gracefully
- **FR006**: System shall persistently store scraped business data in PostgreSQL database
- **FR007**: System shall track scraping job status and provide progress indicators for long-running operations

**Evaluator Module**

- **FR008**: System shall integrate Google Lighthouse CLI to evaluate website performance, SEO, and accessibility metrics
- **FR009**: System shall calculate aggregate website quality score on 0-100 scale combining performance, SEO, and accessibility dimensions
- **FR010**: System shall identify and document specific website problems with categorization (performance, SEO, accessibility)
- **FR011**: System shall automatically flag businesses with scores below 70% for template generation
- **FR012**: System shall store evaluation results and problem analysis linked to each business record

**AI Generator Module**

- **FR013**: System shall integrate OpenAI GPT-4 API for automated website template generation
- **FR014**: System shall automatically trigger template generation when business website score falls below 70%
- **FR015**: System shall inject business-specific data (name, address, phone, services, description) into generated templates
- **FR016**: System shall generate 2-3 template design variants per qualifying business to provide options
- **FR017**: System shall store generated templates (HTML, CSS, JavaScript) in database with metadata linking to source business

**API Layer**

- **FR018**: System shall provide RESTful API endpoints for all operations including business listing, scraping jobs, evaluations, and template generation
- **FR019**: System shall implement JWT-based authentication to secure API access
- **FR020**: System shall support pagination and filtering on business listing endpoints to handle large datasets efficiently
- **FR021**: System shall implement CORS configuration to enable Next.js frontend integration

**Business Cards Display System**

- **FR022**: System shall display businesses in responsive grid layout with animated card components
- **FR023**: System shall show business card content including name, category, description, contact info (email, phone, address), website URL, and color-coded score badge (red <70, green ≥70)
- **FR024**: System shall display problem indicators with icons showing performance, SEO, and accessibility issues
- **FR025**: System shall provide real-time search functionality across all business data fields
- **FR026**: System shall support multi-dimensional filtering by score, location, category, and identified issues

**Template Preview System**

- **FR027**: System shall render AI-generated HTML templates in preview modal or new tab with one-click access
- **FR028**: System shall support navigation between multiple template variants for same business
- **FR029**: System shall display side-by-side comparison view showing old website vs new template
- **FR030**: System shall provide mobile/desktop preview toggle to demonstrate responsive behavior
- **FR031**: System shall highlight improvements panel showing problems solved and enhancements made

**Core User Workflows**

- **FR032**: System shall enable users to initiate scraping jobs with location and niche parameters
- **FR033**: System shall provide export functionality for lead data to support outreach campaigns

### Non-Functional Requirements

- **NFR001 - Performance**: Frontend shall load business card grid in under 2 seconds, API response time for standard queries shall be under 500ms, and template previews shall render in under 3 seconds
- **NFR002 - Scalability**: System shall support scraping of 50+ businesses per hour, complete Lighthouse evaluation in under 60 seconds per site, and generate AI templates in under 2 minutes per business
- **NFR003 - Reliability**: Lighthouse evaluation shall run reliably on 90%+ of discovered websites, and AI template generation shall complete successfully for 80%+ of qualified leads
- **NFR004 - Data Quality**: Business data populated in templates shall maintain 95%+ accuracy, and score calculations shall align with Google Lighthouse standards
- **NFR005 - Security**: System shall implement JWT authentication, API rate limiting, input validation on all endpoints (Pydantic models), sanitization of scraped data, HTTPS for all communications, and environment-based secrets management
- **NFR006 - Usability**: UI/UX shall be intuitive without requiring training documentation, and platform shall support non-technical users
- **NFR007 - Compatibility**: Frontend shall support modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions), be mobile responsive (iOS Safari, Chrome Mobile), and require no IE11 support

---

## User Journeys

### Journey 1: Lead Discovery & Qualification

**Persona:** Web agency owner seeking qualified leads in specific geographic region

**Trigger:** User needs to build pipeline of prospects in Manchester area for plumbing businesses

**Steps:**

1. User navigates to platform and authenticates
2. User initiates new scraping job from dashboard
3. User selects geographic filter: "Manchester" (postcode/city)
4. User selects niche filter: "Plumbing & Heating Services"
5. User confirms job parameters and clicks "Start Scraping"
6. System displays job progress indicator showing businesses discovered in real-time
7. System completes scraping and displays message: "50 businesses discovered"
8. User views business card grid showing discovered businesses
9. For each business, system automatically runs Lighthouse evaluation in background
10. Business cards progressively update with calculated scores as evaluations complete
11. User applies filter: "Score < 70" to view only qualified prospects
12. Business cards re-render showing 32 qualifying businesses with red score badges
13. User reviews business details, noting contact information and identified website problems
14. System automatically flags these 32 businesses for AI template generation

**Decision Points:**
- Geographic and niche selection determines prospect relevance
- Score < 70 filter surfaces highest-value opportunities

**Expected Outcome:** User has qualified database of 32 businesses with poor websites, complete contact data, and detailed problem analysis

---

### Journey 2: Template Preview & Evaluation

**Persona:** Web agency sales lead preparing personalized outreach materials

**Trigger:** User wants to view AI-generated preview for specific prospect before outreach

**Steps:**

1. User browses filtered business card grid showing score < 70 prospects
2. User identifies interesting prospect: "ABC Plumbing - Score 42"
3. User clicks on business card to view details
4. Detail view displays:
   - Complete business information (name, phone, email, address, website URL)
   - Score breakdown (Performance: 38, SEO: 45, Accessibility: 43)
   - Specific problems identified (slow load time, missing meta tags, non-responsive design)
   - "Preview New Website" button showing template generation status
5. If template generation complete, button shows "Preview Available (3 designs)"
6. User clicks "Preview New Website" button
7. System displays template preview modal with:
   - Template variant selector (Design 1, 2, 3)
   - Live HTML rendering in iframe
   - Mobile/Desktop toggle
   - Side-by-side comparison slider (old vs new)
   - Improvements panel showing problems solved
8. User navigates between 3 template variants to evaluate options
9. User toggles mobile preview to verify responsive behavior
10. User reviews improvements panel noting: "95% faster load time, SEO-optimized structure, mobile-responsive design"
11. User decides Design 2 is best fit for this prospect
12. User clicks "Share Preview" to generate shareable link or export preview

**Decision Points:**
- Template quality assessment determines outreach readiness
- Design variant selection personalizes approach for prospect

**Expected Outcome:** User has reviewed professional, personalized website preview and identified best design variant for outreach to this specific prospect

---

### Journey 3: Lead Export for Outreach Campaign

**Persona:** Web agency owner preparing to launch outreach campaign

**Trigger:** User has 25+ qualified leads with previews and wants to export for email campaign

**Steps:**

1. User applies filters to business card grid: "Score < 70" AND "Template Status: Complete"
2. System displays 28 businesses matching criteria
3. User selects specific businesses for outreach using checkboxes (selects 20)
4. User clicks "Export Selected" button
5. System presents export options dialog
6. User selects export format and data fields to include
7. System generates export file containing:
   - Business contact information (name, email, phone, address)
   - Website URL and current score
   - Preview template URL for each business
   - Problem summary and improvement highlights
8. System downloads export file
9. User imports data into email marketing tool or CRM
10. User launches personalized outreach campaign with preview links

**Decision Points:**
- Business selection determines campaign scope
- Export format chosen based on downstream tools

**Expected Outcome:** User has structured data export ready for outreach campaign execution with personalized preview links for each prospect

---

## UX Design Principles

**1. Immediate Visual Impact**
- Every business card and template preview should create "wow" moment through professional design and smooth animations
- Visual proof-of-concept should be instantly compelling - users should immediately understand the value proposition
- Score indicators use clear color coding (red/green) for at-a-glance assessment

**2. Effortless Discovery**
- Lead browsing should feel natural and intuitive with minimal cognitive load
- Multi-dimensional filtering (score, location, category, issues) surfaces relevant prospects quickly
- Real-time search provides instant feedback across all business data

**3. Speed and Responsiveness**
- All interactions feel immediate - no perceived lag between action and response
- Progressive enhancement shows data as it becomes available (scraping progress, evaluation updates)
- Animated transitions provide visual continuity and polish

**4. Transparency and Trust**
- Objective Lighthouse scores provide third-party credibility
- Specific problem identification shows concrete evidence of issues
- Side-by-side comparisons demonstrate clear before/after transformation

**5. Mobile-First Responsive Design**
- All interfaces adapt gracefully across devices (desktop, tablet, mobile)
- Template previews demonstrate responsive behavior with device toggle
- Touch-optimized interactions for mobile usage

---

## User Interface Design Goals

**Platform & Screens**

**Target Platform:** Web application (Next.js 14+)
- Primary: Desktop browsers (Chrome, Firefox, Safari, Edge)
- Secondary: Tablet and mobile responsive support
- No native mobile applications in MVP

**Core Screens:**

1. **Dashboard / Home**
   - Quick stats overview (total businesses, qualified leads, templates generated)
   - Recent scraping jobs with status
   - Quick action buttons to start new scraping job

2. **Business Card Grid**
   - Main working interface showing discovered businesses
   - Filter sidebar with multi-dimensional controls
   - Search bar for real-time filtering
   - Grid layout with animated card components

3. **Business Detail View**
   - Expanded view of single business with complete information
   - Score breakdown visualization
   - Problem analysis with categorization
   - Template preview access

4. **Template Preview Modal**
   - Full-screen or large modal overlay
   - Template variant selector
   - Live HTML rendering in iframe
   - Mobile/desktop toggle
   - Side-by-side comparison view
   - Improvements panel

5. **Scraping Job Configuration**
   - Form to set geographic and niche filters
   - Job submission and progress tracking

**Visual Design Direction**

- **Modern, Professional Aesthetic**: Clean, contemporary design that reflects technical sophistication
- **Animation Language**: Framer Motion for smooth page transitions, GSAP for advanced effects, Lottie for iconography
- **Color System**:
  - Primary: Professional blue/teal for platform branding
  - Success green for scores ≥70
  - Warning red for scores <70
  - Neutral grays for content hierarchy
- **Typography**: Clear, readable sans-serif fonts optimized for data density
- **Card Design**: Elevated cards with subtle shadows, hover states, and smooth transitions
- **Iconography**: Consistent icon system for problem indicators (performance, SEO, accessibility)

**Interaction Patterns**

- **Hover States**: All interactive elements provide visual feedback on hover
- **Loading States**: Skeleton screens and progress indicators for async operations
- **Animations**: Staggered card entry animations, smooth modal transitions, score number animations
- **Keyboard Navigation**: Full keyboard accessibility for power users
- **Responsive Grid**: Adaptive grid layout (4 columns desktop → 2 columns tablet → 1 column mobile)

**Design Constraints**

- Must work within Next.js 14+ App Router architecture
- Tailwind CSS utility-first approach for styling
- Framer Motion for animations and transitions
- Component library: Headless UI or Radix UI for accessible primitives
- Dark mode: Not required for MVP (future consideration)

---

## Epic List

**Epic 1: Project Foundation & Backend Infrastructure**
- **Goal:** Establish project infrastructure, database schema, and core backend API foundation
- **Estimated Stories:** 8-10 stories
- **Delivers:** Working FastAPI application with PostgreSQL database, authentication, and basic API endpoints ready for feature development

**Epic 2: Business Discovery & Scraper Module**
- **Goal:** Build automated scraping system to discover and extract UK business data from directories
- **Estimated Stories:** 7-9 stories
- **Delivers:** Functional scraper that discovers businesses from Checkatrade/Yell with geographic and niche filtering, data validation, and persistent storage

**Epic 3: Website Evaluation & Scoring System**
- **Goal:** Integrate Lighthouse CLI and build custom scoring algorithm to evaluate website quality
- **Estimated Stories:** 6-8 stories
- **Delivers:** Automated website evaluation generating performance/SEO/accessibility scores with detailed problem identification

**Epic 4: AI Template Generation Engine**
- **Goal:** Integrate GPT-4 API to automatically generate personalized website templates for qualifying businesses
- **Estimated Stories:** 7-9 stories
- **Delivers:** AI-powered template generation system producing 2-3 design variants per business with business data injection

**Epic 5: Frontend Business Cards & Discovery UI**
- **Goal:** Build Next.js frontend with business card grid, search, filtering, and detail views
- **Estimated Stories:** 8-10 stories
- **Delivers:** Professional web interface for browsing leads with real-time search, multi-dimensional filtering, and animated business cards

**Epic 6: Template Preview & Comparison System**
- **Goal:** Create template preview interface with variant navigation, side-by-side comparison, and mobile/desktop toggle
- **Estimated Stories:** 6-8 stories
- **Delivers:** Complete template preview experience with live rendering, comparison views, and improvement highlights

**Total Estimated Stories:** 42-54 stories (Level 3 project scale)

> **Note:** Detailed epic breakdown with full story specifications is available in [epics.md](./epics.md)

---

## Out of Scope

**Explicitly NOT in MVP** (Phase 2+ consideration):

**Outreach & Campaign Management:**
- Email automation and automated sending
- Built-in outreach campaign management
- Email open/click tracking
- Automated follow-up sequences
- Integration with email marketing platforms (Mailchimp, SendGrid, etc.)

**Enterprise & Multi-User Features:**
- Multi-user/team collaboration features
- User roles and permissions management
- White-label/multi-tenant capabilities
- Team activity tracking and audit logs

**Advanced Data & Analytics:**
- Analytics dashboard for outreach performance
- Lead conversion funnel tracking
- Template performance analytics (which designs convert best)
- ROI dashboard showing revenue from platform-generated leads
- Geographic heatmaps of lead distribution
- A/B testing of template variants

**CRM & Integration:**
- Bulk export to CSV/CRM platforms
- Native integration with CRM systems (HubSpot, Salesforce, Pipedrive)
- API for third-party integrations
- Webhook notifications for prospect actions
- Sync prospect status and interactions with external systems

**Template Customization:**
- Template customization UI (color schemes, layouts)
- Advanced template editing tools
- Manual template editing capabilities
- Industry-specific template libraries

**Payment & Monetization:**
- Payment processing for lead purchases
- Subscription management for SaaS model
- Usage-based billing

**Platform Expansion:**
- Mobile native applications (iOS, Android)
- International directory support (non-UK)
- Additional scraping sources beyond Checkatrade/Yell
- Social media integration
- Client portal for prospects to view their previews

**MVP Boundaries:**
- Focus remains on UK market only
- Manual outreach process (platform provides leads and previews, user executes outreach)
- Single-user operation (no team collaboration)
- Templates are AI-generated as-is (no customization UI)