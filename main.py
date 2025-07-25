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
    print(f"Received request: {req}")
    
    try:
        task_id = str(uuid.uuid4())
        print(f"Generated task ID: {task_id}")
        
        # Generate panels with Gemini
        print("Calling Gemini service...")
        panels = gemini_service.generate_visual_storyboard(req.prompt, req.style, req.panels)
        print(f"Gemini returned {len(panels)} panels")
        
        if not panels:
            print("Warning: No panels returned from Gemini")
            return VisualResponse(
                panels=[],
                image_paths=[],
                message="Failed to generate panels from prompt"
            )
        
        # Create visual images
        print("Calling visual service...")
        image_paths = visual_service.create_panels(panels, req.style, task_id)
        print(f"Visual service created {len(image_paths)} images")
        
        # Convert to URLs
        img_urls = [f"/outputs/images/{os.path.basename(p)}" for p in image_paths]
        print(f"Generated URLs: {img_urls}")
        
        return VisualResponse(
            panels=panels,
            image_paths=img_urls,
            message=f"Successfully generated {len(panels)} panels and {len(image_paths)} images"
        )
        
    except Exception as e:
        print(f"Error in create_visuals: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/outputs/images/{filename}")
def get_image(filename: str):
    full_path = os.path.join("outputs/images", filename)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404)
    return FileResponse(full_path)
