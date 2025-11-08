"""
Database Query Performance Benchmark Script

Tests query performance with 1000+ records to validate indexing strategy.
Measures execution time for various query patterns used in the API.

Usage:
    python scripts/benchmark_queries.py
"""
import sys
import time
from pathlib import Path
from typing import Dict, List, Callable

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import SessionLocal, engine
from app.models import Business


class QueryBenchmark:
    """Performance benchmark for database queries"""

    def __init__(self, db: Session):
        self.db = db
        self.results: List[Dict] = []

    def measure_query(self, name: str, query_func: Callable, iterations: int = 5) -> Dict:
        """
        Measure query execution time over multiple iterations.

        Args:
            name: Descriptive name for the query
            query_func: Function that executes the query
            iterations: Number of times to run the query (default: 5)

        Returns:
            Dictionary with benchmark results
        """
        print(f"\nBenchmarking: {name}")
        times = []

        for i in range(iterations):
            start_time = time.time()
            result = query_func()
            end_time = time.time()

            execution_time_ms = (end_time - start_time) * 1000
            times.append(execution_time_ms)
            print(f"  Iteration {i+1}: {execution_time_ms:.2f}ms")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        result_data = {
            "query": name,
            "avg_ms": round(avg_time, 2),
            "min_ms": round(min_time, 2),
            "max_ms": round(max_time, 2),
            "status": "PASS" if avg_time < 100 else "FAIL"
        }

        self.results.append(result_data)
        print(f"  Average: {avg_time:.2f}ms | Min: {min_time:.2f}ms | Max: {max_time:.2f}ms")
        print(f"  Status: {result_data['status']} (target: < 100ms)")

        return result_data

    def print_summary(self):
        """Print benchmark summary table"""
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        print(f"{'Query':<50} {'Avg (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12} {'Status':<8}")
        print("-"*80)

        for result in self.results:
            print(f"{result['query']:<50} {result['avg_ms']:<12} {result['min_ms']:<12} {result['max_ms']:<12} {result['status']:<8}")

        print("="*80)

        # Calculate pass/fail statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = total - passed

        print(f"\nTotal Queries: {total}")
        print(f"Passed (< 100ms): {passed}")
        print(f"Failed (>= 100ms): {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print("="*80 + "\n")


def run_benchmarks():
    """Execute all performance benchmarks"""
    db = SessionLocal()
    benchmark = QueryBenchmark(db)

    try:
        print("Starting Database Query Performance Benchmarks")
        print("Target: All queries should execute in < 100ms with 1000+ records")
        print("="*80)

        # Get total count for context
        total_count = db.query(Business).count()
        active_count = db.query(Business).filter(Business.deleted_at.is_(None)).count()
        print(f"\nDatabase Stats:")
        print(f"  Total Businesses: {total_count:,}")
        print(f"  Active Businesses: {active_count:,}")

        # Benchmark 1: List all active businesses with pagination
        benchmark.measure_query(
            "List active businesses (page 1, limit 50)",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None)
            ).order_by(Business.created_at.desc()).limit(50).all()
        )

        # Benchmark 2: List businesses sorted by creation date
        benchmark.measure_query(
            "List businesses sorted by created_at DESC (limit 100)",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None)
            ).order_by(Business.created_at.desc()).limit(100).all()
        )

        # Benchmark 3: Filter by score (uses ix_businesses_score)
        benchmark.measure_query(
            "Filter businesses by score >= 80",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None),
                Business.score >= 80
            ).all()
        )

        # Benchmark 4: Filter by location (uses ix_businesses_location)
        benchmark.measure_query(
            "Filter businesses by location = 'London'",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None),
                Business.location == "London"
            ).all()
        )

        # Benchmark 5: Filter by category (uses ix_businesses_category)
        benchmark.measure_query(
            "Filter businesses by category = 'Plumbing'",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None),
                Business.category == "Plumbing"
            ).all()
        )

        # Benchmark 6: Composite filter - score + location (uses composite index)
        benchmark.measure_query(
            "Filter by score >= 70 AND location = 'Manchester'",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None),
                Business.score >= 70,
                Business.location == "Manchester"
            ).all()
        )

        # Benchmark 7: Composite filter - category + score (uses composite index)
        benchmark.measure_query(
            "Filter by category = 'Electrical' AND score >= 60",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None),
                Business.category == "Electrical",
                Business.score >= 60
            ).all()
        )

        # Benchmark 8: Count active businesses (uses ix_businesses_deleted_at)
        benchmark.measure_query(
            "Count active businesses",
            lambda: db.query(func.count(Business.id)).filter(
                Business.deleted_at.is_(None)
            ).scalar()
        )

        # Benchmark 9: Count businesses by category (uses ix_businesses_category)
        benchmark.measure_query(
            "Count businesses by category = 'Construction'",
            lambda: db.query(func.count(Business.id)).filter(
                Business.deleted_at.is_(None),
                Business.category == "Construction"
            ).scalar()
        )

        # Benchmark 10: Complex filter with sorting
        benchmark.measure_query(
            "Complex: score >= 50, location = 'London', sorted by created_at",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None),
                Business.score >= 50,
                Business.location == "London"
            ).order_by(Business.created_at.desc()).limit(50).all()
        )

        # Benchmark 11: Search by email domain (uses ix_businesses_email)
        benchmark.measure_query(
            "Search businesses with email LIKE '%@%.co.uk'",
            lambda: db.query(Business).filter(
                Business.deleted_at.is_(None),
                Business.email.like("%.co.uk")
            ).limit(100).all()
        )

        # Benchmark 12: Get business by ID (uses primary key)
        first_business = db.query(Business).first()
        if first_business:
            benchmark.measure_query(
                "Get single business by ID (primary key lookup)",
                lambda: db.query(Business).filter(
                    Business.id == first_business.id
                ).first()
            )

        # Print summary
        benchmark.print_summary()

        # Check if all benchmarks passed
        all_passed = all(r['status'] == 'PASS' for r in benchmark.results)

        if all_passed:
            print("SUCCESS: All queries executed within performance targets!")
            return 0
        else:
            print("WARNING: Some queries exceeded 100ms target. Consider further optimization.")
            return 1

    except Exception as e:
        print(f"\nError during benchmarking: {e}")
        import traceback
        traceback.print_exc()
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    exit_code = run_benchmarks()
    sys.exit(exit_code)
