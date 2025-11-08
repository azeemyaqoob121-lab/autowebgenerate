"""Evaluation Models - Website performance evaluation and problem tracking"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class ProblemType(enum.Enum):
    """Problem categories from Lighthouse evaluation"""
    performance = "performance"
    seo = "seo"
    accessibility = "accessibility"
    best_practices = "best-practices"


class ProblemSeverity(enum.Enum):
    """Severity levels for evaluation problems"""
    critical = "critical"
    major = "major"
    minor = "minor"


class Evaluation(Base):
    """
    Website evaluation results from Google Lighthouse

    Stores performance metrics, scores, and full Lighthouse report data.
    One business can have multiple evaluations over time to track improvements.
    """
    __tablename__ = "evaluations"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign Key to Business
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)

    # Lighthouse Scores (0-100 scale)
    performance_score = Column(Float, nullable=False)
    seo_score = Column(Float, nullable=False)
    accessibility_score = Column(Float, nullable=False)
    aggregate_score = Column(Float, nullable=False, index=True)

    # Full Lighthouse Report (JSON structure)
    lighthouse_data = Column(JSONB, nullable=False)

    # Timestamp
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    business = relationship("Business", back_populates="evaluations")
    problems = relationship("EvaluationProblem", back_populates="evaluation", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<Evaluation(id={self.id}, business_id={self.business_id}, "
                f"aggregate_score={self.aggregate_score}, evaluated_at={self.evaluated_at})>")


class EvaluationProblem(Base):
    """
    Specific problems identified during website evaluation

    Tracks individual issues found by Lighthouse with severity classification.
    Enables detailed problem analysis and reporting.
    """
    __tablename__ = "evaluation_problems"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign Key to Evaluation
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Problem Details
    problem_type = Column(SQLEnum(ProblemType), nullable=False, index=True)
    description = Column(Text, nullable=False)
    severity = Column(SQLEnum(ProblemSeverity), nullable=False, index=True)

    # Relationship
    evaluation = relationship("Evaluation", back_populates="problems")

    def __repr__(self):
        return (f"<EvaluationProblem(id={self.id}, type={self.problem_type.value}, "
                f"severity={self.severity.value})>")
