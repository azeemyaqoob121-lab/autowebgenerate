"""Business Model - Represents UK businesses discovered through scraping"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..database import Base


class Business(Base):
    """
    Business entity representing a discovered UK business

    Stores business contact information, website URL, and evaluation scores.
    Primary source of lead data for the AutoWeb Outreach AI platform.
    """
    __tablename__ = "businesses"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Business Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True, index=True)

    # Evaluation Score (aggregate from Lighthouse evaluation)
    score = Column(Integer, nullable=True, index=True)

    # Scraped Website Data (COMPLETE website clone data)
    # Stores: raw_html, images, videos, fonts, colors, components, structure, content
    scraped_data = Column(JSONB, nullable=True, doc="Complete scraped website data for cloning")

    # Enhanced Scraping Fields (Story 4.10)
    scraped_html = Column(Text, nullable=True, doc="Complete HTML document from business website")
    scraped_css = Column(Text, nullable=True, doc="Extracted inline and internal CSS")
    external_css_urls = Column(JSONB, nullable=True, doc="Array of external CSS file URLs")
    image_urls = Column(JSONB, nullable=True, doc="Array of all image src URLs")
    logo_urls = Column(JSONB, nullable=True, doc="Array of logo image URLs")
    video_urls = Column(JSONB, nullable=True, doc="Array of video src URLs and iframe embeds")
    map_embeds = Column(JSONB, nullable=True, doc="Array of map iframe embeds")
    color_palette = Column(JSONB, nullable=True, doc="Array of hex color codes from CSS")
    component_count = Column(Integer, nullable=True, doc="Count of major HTML sections/components")
    component_structure = Column(JSONB, nullable=True, doc="Detailed structure of HTML components")
    scraping_completed_at = Column(DateTime, nullable=True, doc="Timestamp when scraping completed")
    scraping_error = Column(Text, nullable=True, doc="Error message if scraping failed")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True, doc="Soft delete timestamp")

    # Relationships (will be populated when other models are created)
    evaluations = relationship("Evaluation", back_populates="business", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="business", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Business(id={self.id}, name='{self.name}', website='{self.website_url}', score={self.score})>"


# Additional composite index for common query patterns
Index('ix_business_score_location', Business.score, Business.location)
Index('ix_business_category_score', Business.category, Business.score)
