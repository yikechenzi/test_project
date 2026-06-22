from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class TestType(str, enum.Enum):
    BLACK_BOX = "black_box"
    WHITE_BOX = "white_box"
    API = "api"
    UI = "ui"


class TestPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    test_type = Column(Enum(TestType), default=TestType.BLACK_BOX, nullable=False)
    priority = Column(Enum(TestPriority), default=TestPriority.MEDIUM, nullable=False)
    script_content = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="test_cases")
    creator = relationship("User", back_populates="created_test_cases")
    test_executions = relationship("TestExecution", back_populates="test_case")
    
    def __repr__(self):
        return f"<TestCase(id={self.id}, name='{self.name}', type='{self.test_type}')>"