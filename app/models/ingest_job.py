import uuid

from sqlalchemy import (
    Column, Text, DateTime, ForeignKey,
    String, text, Enum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.extension import Base


class IngestJob(Base):
    __tablename__ = "ingest_jobs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False
    )

    submitted_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    raw_text = Column(Text, nullable=False)

    status = Column(
        Enum("pending", "processing", "done", "failed", name="ingest_status"),
        default="pending",
        nullable=False
    )

    result = Column(JSONB)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # relationships
    group = relationship("Group", backref="ingest_jobs", passive_deletes=True)
    submitter = relationship("User", backref="ingest_jobs", passive_deletes=True)