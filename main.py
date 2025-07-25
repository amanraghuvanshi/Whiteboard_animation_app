from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import uuid
import os

from models.schemas import VisualRequest, VisualResponse
from services.gemini_service import GeminiService
from services.visual_service import VisualService

app = FastAPI()
gemini_service = GeminiService()
visual_service = VisualService()

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h2>Whiteboard Visual Generator</h2>"

@app.post("/api/create-visuals", response_model=VisualResponse)
def create_visuals(req: VisualRequest):
    task_id = str(uuid.uuid4())
    panels = gemini_service.generate_visual_storyboard(req.prompt, req.style, req.panels)
    image_paths = visual_service.create_panels(panels, req.style, task_id)
    img_urls = [f"/outputs/images/{os.path.basename(p)}" for p in image_paths]
    return VisualResponse(
        panels=panels,
        image_paths=img_urls,
        message="Panels generated successfully"
    )

@app.get("/outputs/images/{filename}")
def get_image(filename: str):
    full_path = os.path.join("outputs/images", filename)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404)
    return FileResponse(full_path)
