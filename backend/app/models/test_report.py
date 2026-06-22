from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class TestReport(Base):
    __tablename__ = "test_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    summary = Column(JSON, nullable=True)  # JSON summary of test results
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    error_tests = Column(Integer, default=0)
    pass_rate = Column(Integer, default=0)  # Percentage
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    report_path = Column(String(500), nullable=True)  # Path to HTML/PDF report
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="test_reports")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<TestReport(id={self.id}, title='{self.title}')>"
    
    @property
    def success_rate(self):
        if self.total_tests == 0:
            return 0
        return round((self.passed_tests / self.total_tests) * 100, 2)