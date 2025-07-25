from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class VisualStyle(str, Enum):
    WHITEBOARD = "whiteboard"
    SKETCH = "sketch"
    INFOGRAPHIC = "infographic"
    MINIMAL = "minimal"

class VisualRequest(BaseModel):
    prompt: str = Field(..., min_length=10)
    style: VisualStyle = VisualStyle.WHITEBOARD
    panels: Optional[int] = Field(default=4, ge=1, le=9)

class VisualPanel(BaseModel):
    sequence: int
    title: str
    description: str
    visual_elements: List[str]
    text_content: str

class VisualResponse(BaseModel):
    panels: List[VisualPanel]
    image_paths: List[str]
    message: str
