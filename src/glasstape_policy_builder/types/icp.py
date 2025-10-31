"""Simple ICP (Intermediate Canonical Policy) types."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EffectType(str, Enum):
    """Cerbos policy effect types."""
    ALLOW = "EFFECT_ALLOW"
    DENY = "EFFECT_DENY"


class ICPMetadata(BaseModel):
    """Policy metadata."""
    name: str = Field(..., description="Policy name (snake_case)")
    description: str = Field(..., description="Policy description")
    resource: str = Field(..., description="Resource type")
    topics: List[str] = Field(default_factory=list, description="Content topics for governance")
    blocked_topics: List[str] = Field(default_factory=list, description="Explicitly blocked topics")
    safety_category: Optional[str] = Field(default=None, description="Content safety rating: G|PG|PG_13|R|adult_content")
    compliance: Optional[List[str]] = Field(default_factory=list, description="Compliance frameworks")
    tags: Optional[List[str]] = Field(default_factory=list, description="Policy tags")


class ICPRule(BaseModel):
    """Policy rule definition."""
    actions: List[str] = Field(..., description="Actions this rule applies to")
    effect: EffectType = Field(..., description="Allow or deny effect")
    conditions: List[str] = Field(default_factory=list, description="CEL expressions")
    roles: Optional[List[str]] = Field(default=None, description="Required roles")
    description: str = Field(default="", description="Rule description")


class ICPPolicy(BaseModel):
    """Policy definition."""
    resource: str = Field(..., description="Resource type")
    version: str = Field(default="1.0.0", description="Policy version")
    rules: List[ICPRule] = Field(..., description="Policy rules")


class ICPTestInput(BaseModel):
    """Test case input."""
    principal: Dict[str, Any] = Field(..., description="Principal with id and attributes")
    resource: Dict[str, Any] = Field(..., description="Resource with id and attributes")
    actions: List[str] = Field(..., description="Actions to test")


class ICPTest(BaseModel):
    """Policy test case."""
    name: str = Field(..., description="Test name")
    category: str = Field(..., description="Test category: positive, negative, boundary, or adversarial")
    input: ICPTestInput = Field(..., description="Test input")
    expected: EffectType = Field(..., description="Expected effect")
    description: str = Field(default="", description="Test description")


class SimpleICP(BaseModel):
    """Simple Intermediate Canonical Policy."""
    version: str = Field(default="1.0.0", description="ICP format version")
    metadata: ICPMetadata = Field(..., description="Policy metadata")
    policy: ICPPolicy = Field(..., description="Policy definition")
    tests: List[ICPTest] = Field(..., description="Test cases")