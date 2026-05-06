import uuid

from sqlalchemy import (
    Column, String, Text, Date, Time, Boolean,
    DateTime, ForeignKey, SmallInteger, text, Index, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.extension import Base


class Deadline(Base):
    __tablename__ = "deadlines"

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

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    title = Column(String(255), nullable=False)
    description = Column(Text)

    due_date = Column(Date, nullable=False)
    due_time = Column(Time)

    # Better as Enum (strict + safer)
    category = Column(
        Enum("exam", "assignment", "project", "quiz", "other", name="deadline_category"),
        nullable=False
    )

    weight = Column(SmallInteger, default=3)

    subject = Column(String(100))

    source = Column(
        Enum("manual", "email_paste", "syllabus_paste", name="deadline_source"),
        default="manual"
    )

    raw_input = Column(Text)

    is_completed = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # relationships
    group = relationship("Group", backref="deadlines", passive_deletes=True)
    creator = relationship("User", backref="created_deadlines", passive_deletes=True)

    # indexes
    __table_args__ = (
        Index("idx_deadlines_group_due", "group_id", "due_date"),
        Index("idx_deadlines_due_date", "due_date"),
    )