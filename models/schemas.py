# models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class VisualStyle(str, Enum):
    WHITEBOARD = "whiteboard"
    SKETCH = "sketch"
    INFOGRAPHIC = "infographic"
    MINIMAL = "minimal"

class ImageGenerationStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class VisualRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000)
    style: VisualStyle = VisualStyle.WHITEBOARD
    panels: Optional[int] = Field(default=4, ge=1, le=9)
    high_quality: Optional[bool] = Field(default=True)  # Use Imagen v4 high quality mode

class VisualPanel(BaseModel):
    sequence: int
    title: str
    description: str
    visual_elements: List[str]
    text_content: str
    image_generation_status: Optional[ImageGenerationStatus] = ImageGenerationStatus.PENDING
    image_generation_prompt: Optional[str] = None

class VisualResponse(BaseModel):
    panels: List[VisualPanel]
    image_paths: List[str]
    message: str
    generation_stats: Optional[dict] = None

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    result: Optional[dict] = None
