"""Tests for SQLAlchemy Database Models"""
import pytest
from datetime import datetime
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import (
    Business,
    Evaluation,
    EvaluationProblem,
    ProblemType,
    ProblemSeverity,
    Template
)


# Test database URL (PostgreSQL test database)
TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/autoweb_test_db"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def sample_business(db_session):
    """Create a sample business for testing"""
    business = Business(
        id=uuid.uuid4(),
        name="Test Business Ltd",
        email="contact@testbusiness.co.uk",
        phone="+44 20 1234 5678",
        address="123 Test Street, London",
        website_url="https://testbusiness.co.uk",
        category="Plumbing",
        description="Professional plumbing services in London",
        location="London",
        score=65
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)
    return business


class TestBusinessModel:
    """Test cases for Business model"""

    def test_create_business(self, db_session):
        """Test creating a new business"""
        business = Business(
            id=uuid.uuid4(),
            name="ABC Plumbers",
            website_url="https://abcplumbers.co.uk",
            email="info@abcplumbers.co.uk",
            phone="+44 20 9876 5432",
            category="Plumbing",
            location="Manchester"
        )

        db_session.add(business)
        db_session.commit()

        assert business.id is not None
        assert business.name == "ABC Plumbers"
        assert business.created_at is not None
        assert business.updated_at is not None

    def test_business_unique_website_url(self, db_session, sample_business):
        """Test that website_url must be unique"""
        duplicate_business = Business(
            id=uuid.uuid4(),
            name="Duplicate Business",
            website_url=sample_business.website_url,  # Same URL
        )

        db_session.add(duplicate_business)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()

    def test_business_relationships(self, db_session, sample_business):
        """Test business relationships with evaluations and templates"""
        # Create evaluation
        evaluation = Evaluation(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            performance_score=75.5,
            seo_score=80.0,
            accessibility_score=70.0,
            aggregate_score=75.2,
            lighthouse_data={"categories": {"performance": {"score": 0.755}}}
        )
        db_session.add(evaluation)

        # Create template
        template = Template(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            html_content="<html><body>Test</body></html>",
            css_content="body { margin: 0; }",
            variant_number=1,
            improvements_made={"performance": ["Optimized images"]}
        )
        db_session.add(template)
        db_session.commit()

        db_session.refresh(sample_business)

        assert len(sample_business.evaluations) == 1
        assert len(sample_business.templates) == 1
        assert sample_business.evaluations[0].aggregate_score == 75.2

    def test_business_cascade_delete(self, db_session, sample_business):
        """Test that deleting business cascades to evaluations and templates"""
        # Create related records
        evaluation = Evaluation(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            performance_score=75.5,
            seo_score=80.0,
            accessibility_score=70.0,
            aggregate_score=75.2,
            lighthouse_data={}
        )
        db_session.add(evaluation)
        db_session.commit()

        business_id = sample_business.id

        # Delete business
        db_session.delete(sample_business)
        db_session.commit()

        # Verify evaluations are also deleted
        evaluations = db_session.query(Evaluation).filter_by(business_id=business_id).all()
        assert len(evaluations) == 0


class TestEvaluationModel:
    """Test cases for Evaluation model"""

    def test_create_evaluation(self, db_session, sample_business):
        """Test creating a new evaluation"""
        lighthouse_data = {
            "categories": {
                "performance": {"score": 0.85},
                "seo": {"score": 0.90},
                "accessibility": {"score": 0.75}
            }
        }

        evaluation = Evaluation(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            performance_score=85.0,
            seo_score=90.0,
            accessibility_score=75.0,
            aggregate_score=83.3,
            lighthouse_data=lighthouse_data
        )

        db_session.add(evaluation)
        db_session.commit()

        assert evaluation.id is not None
        assert evaluation.business_id == sample_business.id
        assert evaluation.aggregate_score == 83.3
        assert evaluation.lighthouse_data["categories"]["performance"]["score"] == 0.85

    def test_evaluation_relationship_to_business(self, db_session, sample_business):
        """Test evaluation -> business relationship"""
        evaluation = Evaluation(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            performance_score=70.0,
            seo_score=75.0,
            accessibility_score=80.0,
            aggregate_score=75.0,
            lighthouse_data={}
        )

        db_session.add(evaluation)
        db_session.commit()
        db_session.refresh(evaluation)

        assert evaluation.business.id == sample_business.id
        assert evaluation.business.name == sample_business.name


class TestEvaluationProblemModel:
    """Test cases for EvaluationProblem model"""

    def test_create_evaluation_problem(self, db_session, sample_business):
        """Test creating evaluation problems"""
        evaluation = Evaluation(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            performance_score=60.0,
            seo_score=65.0,
            accessibility_score=55.0,
            aggregate_score=60.0,
            lighthouse_data={}
        )
        db_session.add(evaluation)
        db_session.commit()

        problem = EvaluationProblem(
            id=uuid.uuid4(),
            evaluation_id=evaluation.id,
            problem_type=ProblemType.performance,
            description="Large image sizes causing slow load times",
            severity=ProblemSeverity.critical
        )

        db_session.add(problem)
        db_session.commit()

        assert problem.id is not None
        assert problem.problem_type == ProblemType.performance
        assert problem.severity == ProblemSeverity.critical

    def test_problem_enums(self, db_session, sample_business):
        """Test that enum values are properly stored"""
        evaluation = Evaluation(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            performance_score=60.0,
            seo_score=70.0,
            accessibility_score=65.0,
            aggregate_score=65.0,
            lighthouse_data={}
        )
        db_session.add(evaluation)
        db_session.commit()

        # Test all problem types
        problem_types = [
            (ProblemType.performance, ProblemSeverity.critical),
            (ProblemType.seo, ProblemSeverity.major),
            (ProblemType.accessibility, ProblemSeverity.minor),
            (ProblemType.best_practices, ProblemSeverity.major),
        ]

        for ptype, severity in problem_types:
            problem = EvaluationProblem(
                id=uuid.uuid4(),
                evaluation_id=evaluation.id,
                problem_type=ptype,
                description=f"Test {ptype.value} problem",
                severity=severity
            )
            db_session.add(problem)

        db_session.commit()
        db_session.refresh(evaluation)

        assert len(evaluation.problems) == 4


class TestTemplateModel:
    """Test cases for Template model"""

    def test_create_template(self, db_session, sample_business):
        """Test creating a template"""
        improvements = {
            "performance": ["Optimized images", "Lazy loading"],
            "seo": ["Added meta tags", "Improved structure"],
            "design": ["Modern layout", "Responsive grid"]
        }

        template = Template(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            html_content="<!DOCTYPE html><html><body>Content</body></html>",
            css_content="body { font-family: Arial; }",
            js_content="console.log('Loaded');",
            improvements_made=improvements,
            variant_number=1
        )

        db_session.add(template)
        db_session.commit()

        assert template.id is not None
        assert template.variant_number == 1
        assert "performance" in template.improvements_made

    def test_template_variants(self, db_session, sample_business):
        """Test creating multiple template variants for same business"""
        for variant in [1, 2, 3]:
            template = Template(
                id=uuid.uuid4(),
                business_id=sample_business.id,
                html_content=f"<html>Variant {variant}</html>",
                css_content="body { margin: 0; }",
                variant_number=variant,
                improvements_made={}
            )
            db_session.add(template)

        db_session.commit()
        db_session.refresh(sample_business)

        assert len(sample_business.templates) == 3
        variant_numbers = [t.variant_number for t in sample_business.templates]
        assert set(variant_numbers) == {1, 2, 3}

    def test_template_optional_js(self, db_session, sample_business):
        """Test that js_content is optional"""
        template = Template(
            id=uuid.uuid4(),
            business_id=sample_business.id,
            html_content="<html></html>",
            css_content="body {}",
            js_content=None,  # Optional
            variant_number=1,
            improvements_made={}
        )

        db_session.add(template)
        db_session.commit()

        assert template.js_content is None


class TestModelIntegration:
    """Integration tests for all models working together"""

    def test_complete_workflow(self, db_session):
        """Test complete workflow: business -> evaluation -> problems -> template"""
        # 1. Create business
        business = Business(
            id=uuid.uuid4(),
            name="Complete Test Business",
            website_url="https://completetest.co.uk",
            category="Construction",
            location="Birmingham",
            score=None  # Not yet evaluated
        )
        db_session.add(business)
        db_session.commit()

        # 2. Create evaluation
        evaluation = Evaluation(
            id=uuid.uuid4(),
            business_id=business.id,
            performance_score=62.0,
            seo_score=58.0,
            accessibility_score=60.0,
            aggregate_score=60.0,
            lighthouse_data={"categories": {}}
        )
        db_session.add(evaluation)
        db_session.commit()

        # 3. Update business score
        business.score = int(evaluation.aggregate_score)
        db_session.commit()

        # 4. Create problems
        problems = [
            EvaluationProblem(
                id=uuid.uuid4(),
                evaluation_id=evaluation.id,
                problem_type=ProblemType.performance,
                description="Unoptimized images",
                severity=ProblemSeverity.critical
            ),
            EvaluationProblem(
                id=uuid.uuid4(),
                evaluation_id=evaluation.id,
                problem_type=ProblemType.seo,
                description="Missing meta descriptions",
                severity=ProblemSeverity.major
            )
        ]
        for problem in problems:
            db_session.add(problem)
        db_session.commit()

        # 5. Generate templates (since score < 70)
        for variant in [1, 2, 3]:
            template = Template(
                id=uuid.uuid4(),
                business_id=business.id,
                html_content=f"<html>Variant {variant}</html>",
                css_content="body { margin: 0; }",
                variant_number=variant,
                improvements_made={
                    "performance": ["Optimized images"],
                    "seo": ["Added meta tags"]
                }
            )
            db_session.add(template)
        db_session.commit()

        # Verify everything is connected
        db_session.refresh(business)
        assert business.score == 60
        assert len(business.evaluations) == 1
        assert len(business.templates) == 3
        assert len(business.evaluations[0].problems) == 2
