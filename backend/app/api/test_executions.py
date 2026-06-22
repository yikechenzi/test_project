from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, check_project_permission
from app.models.test_execution import TestExecution, ExecutionStatus
from app.models.test_case import TestCase
from app.models.user import User

router = APIRouter()


class TestExecutionResponse(BaseModel):
    id: int
    test_case_id: int
    executed_by: Optional[int]
    status: ExecutionStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[float]
    logs: Optional[str]
    error_message: Optional[str]
    screenshot_path: Optional[str]
    video_path: Optional[str]
    environment: Optional[str]
    browser_version: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TestExecutionResponse])
async def get_test_executions(
    test_case_id: Optional[int] = None,
    status: Optional[ExecutionStatus] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test executions list
    """
    query = db.query(TestExecution)
    
    if test_case_id:
        # Check permissions
        test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
        if test_case and not check_project_permission(current_user, test_case.project_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        query = query.filter(TestExecution.test_case_id == test_case_id)
    
    if status:
        query = query.filter(TestExecution.status == status)
    
    executions = query.order_by(TestExecution.created_at.desc()).offset(skip).limit(limit).all()
    return executions


@router.get("/{execution_id}", response_model=TestExecutionResponse)
async def get_test_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test execution by ID
    """
    execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test execution not found"
        )
    
    # Check permissions
    test_case = db.query(TestCase).filter(TestCase.id == execution.test_case_id).first()
    if test_case and not check_project_permission(current_user, test_case.project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return execution


@router.post("/{test_case_id}/execute")
async def execute_test_case(
    test_case_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute test case
    """
    # Get test case
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    
    # Check permissions
    if not check_project_permission(current_user, test_case.project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create execution record
    execution = TestExecution(
        test_case_id=test_case_id,
        executed_by=current_user.id,
        status=ExecutionStatus.PENDING,
        start_time=datetime.utcnow()
    )
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Run test in background
    background_tasks.add_task(
        run_test_execution,
        execution.id,
        test_case.script_content,
        test_case.test_type
    )
    
    return {
        "message": "Test execution started",
        "execution_id": execution.id,
        "status": execution.status
    }


async def run_test_execution(execution_id: int, script_content: str, test_type: str):
    """
    Run test execution in background
    """
    from app.core.database import SessionLocal
    from app.services.test_runner import TestRunner
    
    db = SessionLocal()
    try:
        # Update status to running
        execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
        execution.status = ExecutionStatus.RUNNING
        db.commit()
        
        # Run test
        runner = TestRunner()
        result = await runner.run_test(script_content, test_type)
        
        # Update execution with results
        execution.end_time = datetime.utcnow()
        execution.duration = (execution.end_time - execution.start_time).total_seconds()
        execution.status = ExecutionStatus.PASSED if result["success"] else ExecutionStatus.FAILED
        execution.logs = result.get("logs")
        execution.error_message = result.get("error")
        execution.screenshot_path = result.get("screenshot_path")
        execution.video_path = result.get("video_path")
        
        db.commit()
        
    except Exception as e:
        # Update execution with error
        execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
        execution.status = ExecutionStatus.ERROR
        execution.error_message = str(e)
        execution.end_time = datetime.utcnow()
        if execution.start_time:
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
        db.commit()
        
    finally:
        db.close()


@router.post("/{execution_id}/cancel")
async def cancel_test_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel test execution
    """
    execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test execution not found"
        )
    
    # Check permissions
    test_case = db.query(TestCase).filter(TestCase.id == execution.test_case_id).first()
    if test_case and not check_project_permission(current_user, test_case.project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Can only cancel pending or running executions
    if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed execution"
        )
    
    execution.status = ExecutionStatus.CANCELLED
    execution.end_time = datetime.utcnow()
    if execution.start_time:
        execution.duration = (execution.end_time - execution.start_time).total_seconds()
    
    db.commit()
    
    return {"message": "Test execution cancelled"}


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get execution logs
    """
    execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test execution not found"
        )
    
    # Check permissions
    test_case = db.query(TestCase).filter(TestCase.id == execution.test_case_id).first()
    if test_case and not check_project_permission(current_user, test_case.project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return {
        "execution_id": execution.id,
        "logs": execution.logs,
        "error_message": execution.error_message
    }