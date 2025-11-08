# Story 5.9: Scraping Job Management UI

**Epic:** Epic 5 - Frontend Business Cards & Discovery UI
**Status:** ⏳ Pending

## User Story

As a user,
I want to initiate and track scraping jobs,
So that I can discover new businesses on demand.

## Acceptance Criteria

- [ ] "New Scraping Job" page created with form
- [ ] Form fields: location (text input), category (dropdown with common categories)
- [ ] Form validation ensures required fields filled
- [ ] Submit triggers POST /api/scraping-jobs and redirects to job status page
- [ ] Job status page shows: progress bar, businesses found count, current status
- [ ] Status page polls GET /api/scraping-jobs/{id} every 5 seconds for updates
- [ ] Completion message shown when job finishes
- [ ] "View Results" button navigates to business grid filtered to new businesses
- [ ] Job list page shows all previous jobs with status and results count
