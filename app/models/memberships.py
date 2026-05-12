import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.extension import Base


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False
    )

    role = Column(String(20), default="member")

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_user_group"),
    )

    group_name = Column(String(100), nullable=True)

    # relationships
    user = relationship("User", backref="memberships", passive_deletes=True)
    group = relationship("Group", backref="memberships", passive_deletes=True)