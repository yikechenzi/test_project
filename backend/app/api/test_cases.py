from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, check_project_permission
from app.models.test_case import TestCase, TestType, TestPriority
from app.models.user import User

router = APIRouter()


class TestCaseCreate(BaseModel):
    project_id: int
    name: str
    description: Optional[str] = None
    test_type: TestType = TestType.BLACK_BOX
    priority: TestPriority = TestPriority.MEDIUM
    script_content: str
    expected_result: Optional[str] = None
    tags: Optional[str] = None


class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    test_type: Optional[TestType] = None
    priority: Optional[TestPriority] = None
    script_content: Optional[str] = None
    expected_result: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None


class TestCaseResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str]
    test_type: TestType
    priority: TestPriority
    script_content: str
    expected_result: Optional[str]
    tags: Optional[str]
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TestCaseResponse])
async def get_test_cases(
    project_id: Optional[int] = None,
    test_type: Optional[TestType] = None,
    priority: Optional[TestPriority] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test cases list
    """
    query = db.query(TestCase)
    
    if project_id:
        # Check permissions
        if not check_project_permission(current_user, project_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        query = query.filter(TestCase.project_id == project_id)
    else:
        # If no project_id specified, get all test cases for user's projects
        if current_user.role != "admin":
            from app.models.project import UserProject
            user_project_ids = db.query(UserProject.project_id).filter(
                UserProject.user_id == current_user.id
            ).all()
            project_ids = [p[0] for p in user_project_ids]
            query = query.filter(TestCase.project_id.in_(project_ids))
    
    if test_type:
        query = query.filter(TestCase.test_type == test_type)
    if priority:
        query = query.filter(TestCase.priority == priority)
    
    test_cases = query.offset(skip).limit(limit).all()
    return test_cases


@router.get("/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(
    test_case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test case by ID
    """
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
    
    return test_case


@router.post("/", response_model=TestCaseResponse)
async def create_test_case(
    test_case_data: TestCaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new test case
    """
    # Check permissions
    if not check_project_permission(current_user, test_case_data.project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    test_case = TestCase(
        project_id=test_case_data.project_id,
        name=test_case_data.name,
        description=test_case_data.description,
        test_type=test_case_data.test_type,
        priority=test_case_data.priority,
        script_content=test_case_data.script_content,
        expected_result=test_case_data.expected_result,
        tags=test_case_data.tags,
        created_by=current_user.id
    )
    
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    
    return test_case


@router.put("/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: int,
    test_case_data: TestCaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update test case
    """
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
    
    # Update fields
    if test_case_data.name is not None:
        test_case.name = test_case_data.name
    if test_case_data.description is not None:
        test_case.description = test_case_data.description
    if test_case_data.test_type is not None:
        test_case.test_type = test_case_data.test_type
    if test_case_data.priority is not None:
        test_case.priority = test_case_data.priority
    if test_case_data.script_content is not None:
        test_case.script_content = test_case_data.script_content
    if test_case_data.expected_result is not None:
        test_case.expected_result = test_case_data.expected_result
    if test_case_data.tags is not None:
        test_case.tags = test_case_data.tags
    if test_case_data.is_active is not None:
        test_case.is_active = test_case_data.is_active
    
    test_case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(test_case)
    
    return test_case


@router.delete("/{test_case_id}")
async def delete_test_case(
    test_case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete test case
    """
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
    
    # Check if test case has executions
    if test_case.test_executions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete test case with executions"
        )
    
    db.delete(test_case)
    db.commit()
    
    return {"message": "Test case deleted successfully"}


@router.post("/generate-ai")
async def generate_test_case_with_ai(
    project_id: int,
    description: str,
    test_type: TestType = TestType.BLACK_BOX,
    target_url: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate test case using AI
    """
    # Check permissions
    if not check_project_permission(current_user, project_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Use AI service to generate test script
    from app.services.ai_service import ai_service
    
    result = await ai_service.generate_test_script(
        description=description,
        test_type=test_type.value,
        target_url=target_url
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "message": "Test script generated successfully",
        "script": result["script"],
        "description": description,
        "test_type": test_type,
        "model": result.get("model"),
        "tokens_used": result.get("tokens_used")
    }