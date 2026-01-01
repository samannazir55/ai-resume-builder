from pydantic import BaseModel
from typing import List, Optional
import datetime

class CVData(BaseModel):
    """
    Detail of all structured CV fields (mirrors most frontend form fields).
    """
    full_name: str
    email: str
    phone: str
    job_title: str
    summary: str
    experience: str
    education: str
    skills: List[str]
    languages: Optional[str] = None
    certifications: Optional[str] = None

class CVCreate(BaseModel):
    title: str
    data: CVData
    template_id: str = "modern"

class CVUpdate(BaseModel):
    title: Optional[str] = None
    data: Optional[CVData] = None
    template_id: Optional[str] = None

class CVInDB(BaseModel):
    id: int
    user_id: int
    title: str
    template_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

class CV(CVInDB):
    data: CVData
class CVList(BaseModel):
    """List of CVs for a user."""
    cvs: List[CV]

    class Config:
        orm_mode = True
class CVResponse(BaseModel):
    """Unified response schema for CV operations."""
    success: bool
    data: Optional[CV] = None  # Data field for successful responses
    error: Optional[str] = None  # Error message if any

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True  # Automatically strip whitespace from strings
        use_enum_values = True  # Use enum values instead of enum names in the output