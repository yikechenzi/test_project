from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TestExecution(Base):
    __tablename__ = "test_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # Duration in seconds
    logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    screenshot_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    environment = Column(String(100), nullable=True)  # e.g., "chrome", "firefox"
    browser_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_case = relationship("TestCase", back_populates="test_executions")
    executor = relationship("User", back_populates="test_executions")
    
    def __repr__(self):
        return f"<TestExecution(id={self.id}, status='{self.status}')>"
    
    @property
    def is_completed(self):
        return self.status in [
            ExecutionStatus.PASSED,
            ExecutionStatus.FAILED,
            ExecutionStatus.ERROR,
            ExecutionStatus.SKIPPED,
            ExecutionStatus.CANCELLED
        ]