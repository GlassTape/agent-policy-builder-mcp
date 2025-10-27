"""Result types for validation and analysis."""

from typing import List
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Cerbos validation result."""
    success: bool = Field(..., description="Validation success status")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class TestResult(BaseModel):
    """Cerbos test execution result."""
    passed: int = Field(ge=0, description="Number of passed tests")
    failed: int = Field(ge=0, description="Number of failed tests")
    total: int = Field(ge=0, description="Total number of tests")
    details: str = Field(default="", description="Detailed test output")


class RedTeamFinding(BaseModel):
    """Security analysis finding."""
    check: str = Field(..., description="Security check name")
    status: str = Field(..., description="Status: pass, warn, or fail")
    message: str = Field(..., description="Finding description")