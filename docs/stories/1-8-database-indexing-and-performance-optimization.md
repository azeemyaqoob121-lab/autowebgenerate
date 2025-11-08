# Story 1.8: Database Indexing and Performance Optimization

Status: todo

## Story

As a backend developer,
I want to optimize database queries with proper indexing,
So that API responses remain fast as data volume grows.

## Acceptance Criteria

1. Index created on businesses.score for filtering
2. Index created on businesses.location for geographic queries
3. Index created on businesses.category for niche filtering
4. Index created on businesses.created_at for sorting
5. Composite index created on (score, location) for common filter combinations
6. Foreign key indexes verified on all relationship columns
7. Query performance tested with 1000+ business records, all queries < 100ms

## Tasks / Subtasks

- [ ] Audit existing indexes from Story 1.2 (AC: 1-4)
  - [ ] Review `backend/app/models/business.py` for existing indexes
  - [ ] Review initial migration for index definitions
  - [ ] Verify indexes: website_url (unique), score, location, category
  - [ ] Check if created_at index exists (may need to add)
  - [ ] Document current index coverage

- [ ] Create composite indexes for common query patterns (AC: 5)
  - [ ] Identify common filter combinations from business requirements
  - [ ] Add composite index on (score, location) for "low-scoring businesses in region" queries
  - [ ] Add composite index on (category, score) for "low-scoring businesses in niche" queries
  - [ ] Add composite index on (deleted_at, created_at) for listing active businesses chronologically
  - [ ] Consider index on (website_url, deleted_at) for duplicate checking excluding soft-deleted
  - [ ] Generate Alembic migration for new indexes

- [ ] Verify foreign key indexes (AC: 6)
  - [ ] Check evaluations table: business_id should have index (FK index)
  - [ ] Check evaluation_problems table: evaluation_id should have index (FK index)
  - [ ] Check templates table: business_id should have index (FK index)
  - [ ] PostgreSQL creates FK indexes automatically in most cases, verify in database
  - [ ] Add explicit indexes if missing

- [ ] Add indexes for User table (from Story 1.4)
  - [ ] Verify email index (unique) exists on users table
  - [ ] Add index on users.is_active for filtering active users
  - [ ] Add index on users.created_at for user analytics

- [ ] Optimize text search performance
  - [ ] Add GIN index for full-text search on businesses.description (if using ILIKE frequently)
  - [ ] Add trigram indexes for fuzzy search (pg_trgm extension)
  - [ ] Test search query performance before and after indexing
  - [ ] Document when to use GIN vs B-tree indexes

- [ ] Configure database connection pooling
  - [ ] Review pool settings in `backend/app/database.py` (already configured in Story 1.3)
  - [ ] Verify pool_size=5, max_overflow=10 is appropriate for load
  - [ ] Add pool monitoring for connection exhaustion
  - [ ] Test concurrent request handling (simulate 20+ simultaneous requests)

- [ ] Implement query result caching with Redis
  - [ ] Create `backend/app/utils/cache.py` module
  - [ ] Implement Redis caching decorator for expensive queries
  - [ ] Cache business list queries with 5-minute TTL
  - [ ] Cache individual business lookups with 15-minute TTL
  - [ ] Cache evaluation results with 1-hour TTL
  - [ ] Implement cache invalidation on updates/deletes
  - [ ] Test cache hit/miss rates

- [ ] Add database query logging for slow queries
  - [ ] Configure SQLAlchemy event listener for query execution time
  - [ ] Log queries taking longer than 1 second at WARNING level
  - [ ] Include query SQL, parameters, execution time in log
  - [ ] Add query profiling in development environment
  - [ ] Test with complex queries to verify logging works

- [ ] Optimize common queries
  - [ ] Review business list query with filters
  - [ ] Add `.options(joinedload())` for eager loading relationships when needed
  - [ ] Use `.options(load_only())` to select only required columns
  - [ ] Avoid N+1 query problems (load related evaluations/templates efficiently)
  - [ ] Test query execution plans with EXPLAIN ANALYZE

- [ ] Create performance testing dataset
  - [ ] Create seed script: `backend/scripts/seed_database.py`
  - [ ] Generate 1000+ realistic business records
  - [ ] Generate evaluation records for 80% of businesses
  - [ ] Generate template records for businesses with score < 70
  - [ ] Seed with varied locations, categories, scores for testing filters
  - [ ] Make seed script idempotent (can run multiple times)

- [ ] Run performance benchmarks (AC: 7)
  - [ ] Seed database with 1000+ records
  - [ ] Benchmark GET /api/businesses with no filters (should be < 50ms)
  - [ ] Benchmark GET /api/businesses with score filter (should be < 100ms)
  - [ ] Benchmark GET /api/businesses with location filter (should be < 100ms)
  - [ ] Benchmark GET /api/businesses with composite filter (score + location) (should be < 100ms)
  - [ ] Benchmark GET /api/businesses/{id} with related data (should be < 50ms)
  - [ ] Document benchmark results

- [ ] Create Alembic migration for new indexes
  - [ ] Generate migration: `alembic revision -m "add_performance_indexes"`
  - [ ] Add composite indexes to migration
  - [ ] Add any missing FK indexes
  - [ ] Add text search indexes
  - [ ] Test migration up and down (rollback)
  - [ ] Apply migration to test database

- [ ] Document optimization strategies
  - [ ] Create `docs/database-optimization.md`
  - [ ] Document all indexes and their purpose
  - [ ] Explain when to use which index
  - [ ] Document caching strategy
  - [ ] Provide query optimization guidelines for future development
  - [ ] Include benchmark results and performance targets

## Dev Notes

### Learnings from Previous Stories

**From Story 1.5 (Business CRUD - when completed)**
- **Common Filters**: score range, location, category, search text - need optimized indexes
- **Pagination**: All list queries use LIMIT/OFFSET - ensure efficient with large datasets
- **Soft Delete**: deleted_at field used in WHERE clauses - include in composite indexes

**From Story 1.3 (Status: review)**
- **Connection Pool**: Already configured with pool_size=5, max_overflow=10
- **Redis Available**: Redis service in docker-compose, ready for caching
- **Query Logging**: Event listeners already configured for connection pool monitoring

**From Story 1.2 (Status: review)**
- **Existing Indexes**: Business model has indexes on website_url (unique), score, location, category
- **Relationships**: Business → Evaluation (1:many), Business → Template (1:many)
- **Foreign Keys**: Already defined with proper CASCADE behavior

[Source: stories/1-2-postgresql-database-schema-and-models.md#Dev-Agent-Record]

### Project Structure

```
backend/
├── app/
│   ├── models/          # UPDATE: Verify index definitions
│   ├── utils/
│   │   └── cache.py     # NEW: Redis caching utilities
│   └── database.py      # UPDATE: Add slow query logging
├── scripts/
│   └── seed_database.py # NEW: Performance testing data
├── alembic/
│   └── versions/
│       └── xxx_add_performance_indexes.py  # NEW: Migration
└── ...

docs/
└── database-optimization.md  # NEW: Optimization guide
```

### Technical Constraints

- **PostgreSQL Version**: 14+ (GIN indexes, JSONB indexing support)
- **Index Size**: Monitor index size vs table size (indexes have overhead)
- **Redis**: For query result caching (already in docker-compose)
- **Performance Target**: < 100ms for filtered queries, < 50ms for simple lookups (per NFR001)
- **Dataset Size**: Test with 1000+ records minimum, plan for 10,000+ growth

### Index Types and Usage

**B-tree Indexes (Default):**
- Best for: Exact matches, range queries, sorting
- Use for: score, location, category, created_at, foreign keys
- Example: `CREATE INDEX idx_business_score ON businesses(score);`

**Composite Indexes:**
- Best for: Multiple column filters used together
- Order matters: Most selective column first
- Example: `CREATE INDEX idx_business_score_location ON businesses(score, location);`
- Covers queries filtering by (score) or (score + location), but NOT just (location)

**Unique Indexes:**
- Enforce uniqueness constraint
- Also provides B-tree index benefits
- Example: `CREATE UNIQUE INDEX idx_business_website ON businesses(website_url);`

**GIN Indexes (Generalized Inverted Index):**
- Best for: Full-text search, JSONB queries, array contains
- Use for: description (if using text search), lighthouse_data JSONB
- Example: `CREATE INDEX idx_business_description_gin ON businesses USING gin(to_tsvector('english', description));`

**Partial Indexes:**
- Index only subset of rows matching condition
- Smaller, faster for common cases
- Example: `CREATE INDEX idx_active_businesses ON businesses(created_at) WHERE deleted_at IS NULL;`

### Composite Index Strategy

**Common Query Patterns:**
1. **"Find low-scoring businesses in location"**
   - Filter: `score < 70 AND location = 'Manchester'`
   - Index: `(score, location)` or `(location, score)`
   - Choose order based on selectivity

2. **"Find businesses by category with low scores"**
   - Filter: `category = 'Plumbing' AND score < 70`
   - Index: `(category, score)`

3. **"List active businesses by date"**
   - Filter: `deleted_at IS NULL ORDER BY created_at DESC`
   - Index: `(deleted_at, created_at)` (partial index alternative: WHERE deleted_at IS NULL)

**Index Selectivity:**
- More selective column first in composite index
- Selectivity = COUNT(DISTINCT column) / COUNT(*)
- High selectivity (many unique values) = good for leading column
- Low selectivity (few unique values) = better as later column

### Caching Strategy

**Redis Cache Patterns:**

**Cache Keys:**
```
business:list:{filters_hash}:{page}  # Business list queries
business:detail:{business_id}        # Single business lookups
evaluation:latest:{business_id}      # Latest evaluation per business
```

**Cache TTLs:**
- List queries: 5 minutes (frequently updated)
- Business details: 15 minutes (occasionally updated)
- Evaluations: 1 hour (infrequently updated)
- Templates: 1 hour (infrequently updated)

**Cache Invalidation:**
- On business update/delete: Invalidate `business:detail:{id}` and all `business:list:*`
- On evaluation create: Invalidate `evaluation:latest:{business_id}`
- On template create: Invalidate `business:detail:{id}` (includes template_count)

**Implementation:**
```python
from functools import wraps
import redis
import pickle

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def cache_result(key_prefix: str, ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{hash((args, tuple(kwargs.items())))}"
            cached = redis_client.get(cache_key)
            if cached:
                return pickle.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, pickle.dumps(result))
            return result
        return wrapper
    return decorator
```

### Query Optimization Techniques

**Eager Loading (Avoid N+1):**
```python
# BAD: N+1 queries
businesses = db.query(Business).limit(50).all()
for business in businesses:
    print(business.evaluations)  # Separate query for EACH business

# GOOD: Single query with JOIN
from sqlalchemy.orm import joinedload
businesses = db.query(Business).options(
    joinedload(Business.evaluations)
).limit(50).all()
```

**Select Only Needed Columns:**
```python
# BAD: Select all columns
businesses = db.query(Business).all()

# GOOD: Select specific columns
businesses = db.query(Business.id, Business.name, Business.score).all()

# BETTER: Use load_only
from sqlalchemy.orm import load_only
businesses = db.query(Business).options(
    load_only(Business.id, Business.name, Business.score)
).all()
```

**Use Query Pagination Efficiently:**
```python
# Efficient pagination with LIMIT/OFFSET
businesses = db.query(Business).filter(
    Business.deleted_at.is_(None)
).order_by(
    Business.created_at.desc()
).limit(50).offset(page * 50).all()

# Count total separately (only when needed)
total = db.query(func.count(Business.id)).filter(
    Business.deleted_at.is_(None)
).scalar()
```

### Performance Monitoring

**Metrics to Track:**
- Query execution time (p50, p95, p99 percentiles)
- Cache hit rate (target: >80% for list queries)
- Database connection pool usage (target: <50% average)
- Slow query frequency (target: <1% of queries over 1 second)
- Index usage statistics (PostgreSQL pg_stat_user_indexes)

**Monitoring Queries:**
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;

-- Find unused indexes (idx_scan = 0)
SELECT schemaname, tablename, indexname
FROM pg_stat_user_indexes
WHERE schemaname = 'public' AND idx_scan = 0;

-- Check table sizes
SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public';
```

### References

- [Source: docs/epics.md#Story-1.8]
- [Source: docs/PRD.md#NFR001] (Performance requirements)
- PostgreSQL Indexes: https://www.postgresql.org/docs/14/indexes.html
- SQLAlchemy Query Optimization: https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
- Redis Caching: https://redis.io/docs/manual/client-side-caching/

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

<!-- Will be filled during implementation -->

### Debug Log References

<!-- Will be filled during implementation -->

### Completion Notes List

<!-- Will be filled during implementation -->

### File List

<!-- Will be filled during implementation -->

## Change Log

- 2025-11-01: Story created from Epic 1, Story 8 in epics.md
