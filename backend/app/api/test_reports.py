from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, check_project_permission
from app.models.test_report import TestReport
from app.models.test_execution import TestExecution, ExecutionStatus
from app.models.test_case import TestCase
from app.models.user import User

router = APIRouter()


class TestReportResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    summary: Optional[dict]
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    pass_rate: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[int]
    report_path: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TestReportResponse])
async def get_test_reports(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test reports list
    """
    query = db.query(TestReport)
    
    if project_id:
        # Check permissions
        if not check_project_permission(current_user, project_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        query = query.filter(TestReport.project_id == project_id)
    else:
        # If no project_id specified, get all reports for user's projects
        if current_user.role != "admin":
            from app.models.project import UserProject
            user_project_ids = db.query(UserProject.project_id).filter(
                UserProject.user_id == current_user.id
            ).all()
            project_ids = [p[0] for p in user_project_ids]
            query = query.filter(TestReport.project_id.in_(project_ids))
    
    reports = query.order_by(TestReport.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=TestReportResponse)
async def get_test_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test report by ID
    """
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test report not found"
        )
    
    # Check permissions
    if not check_project_permission(current_user, report.project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return report


@router.post("/generate/{project_id}")
async def generate_test_report(
    project_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate test report for project
    """
    # Check permissions
    if not check_project_permission(current_user, project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get all test executions for the project
    from app.models.project import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get test cases for the project
    test_cases = db.query(TestCase).filter(TestCase.project_id == project_id).all()
    test_case_ids = [tc.id for tc in test_cases]
    
    # Get executions for these test cases
    executions = db.query(TestExecution).filter(
        TestExecution.test_case_id.in_(test_case_ids)
    ).all()
    
    # Calculate statistics
    total_tests = len(executions)
    passed_tests = len([e for e in executions if e.status == ExecutionStatus.PASSED])
    failed_tests = len([e for e in executions if e.status == ExecutionStatus.FAILED])
    skipped_tests = len([e for e in executions if e.status == ExecutionStatus.SKIPPED])
    error_tests = len([e for e in executions if e.status == ExecutionStatus.ERROR])
    
    pass_rate = round((passed_tests / total_tests * 100) if total_tests > 0 else 0)
    
    # Calculate duration
    start_times = [e.start_time for e in executions if e.start_time]
    end_times = [e.end_time for e in executions if e.end_time]
    
    start_time = min(start_times) if start_times else None
    end_time = max(end_times) if end_times else None
    duration = int((end_time - start_time).total_seconds()) if start_time and end_time else None
    
    # Create report
    report = TestReport(
        project_id=project_id,
        title=title or f"Test Report - {project.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        description=description,
        summary={
            "total_executions": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "error": error_tests,
            "pass_rate": pass_rate
        },
        total_tests=total_tests,
        passed_tests=passed_tests,
        failed_tests=failed_tests,
        skipped_tests=skipped_tests,
        error_tests=error_tests,
        pass_rate=pass_rate,
        start_time=start_time,
        end_time=end_time,
        duration=duration,
        created_by=current_user.id
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Generate HTML report
    from app.services.report_generator import ReportGenerator
    generator = Generator()
    report_path = await generator.generate_html_report(report, executions)
    
    report.report_path = report_path
    db.commit()
    
    return {
        "message": "Test report generated successfully",
        "report_id": report.id,
        "report_path": report_path
    }


@router.delete("/{report_id}")
async def delete_test_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete test report
    """
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test report not found"
        )
    
    # Check permissions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete report file if exists
    if report.report_path:
        import os
        try:
            os.remove(report.report_path)
        except:
            pass
    
    db.delete(report)
    db.commit()
    
    return {"message": "Test report deleted successfully"}


@router.get("/{report_id}/details")
async def get_report_details(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed report information
    """
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test report not found"
        )
    
    # Check permissions
    if not check_project_permission(current_user, report.project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get all executions for the project
    from app.models.project import Project
    test_cases = db.query(TestCase).filter(TestCase.project_id == report.project_id).all()
    test_case_ids = [tc.id for tc in test_cases]
    
    executions = db.query(TestExecution).filter(
        TestExecution.test_case_id.in_(test_case_ids)
    ).all()
    
    # Build detailed results
    details = []
    for tc in test_cases:
        tc_executions = [e for e in executions if e.test_case_id == tc.id]
        latest_execution = tc_executions[0] if tc_executions else None
        
        details.append({
            "test_case_id": tc.id,
            "test_case_name": tc.name,
            "test_type": tc.test_type,
            "priority": tc.priority,
            "latest_status": latest_execution.status if latest_execution else "not_executed",
            "execution_count": len(tc_executions),
            "last_executed": latest_execution.created_at if latest_execution else None
        })
    
    return {
        "report": report,
        "details": details
    }