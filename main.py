from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uuid
import os

from models.schemas import VisualRequest, VisualResponse
from services.gemini_service import GeminiService
from services.visual_service import VisualService
from utils.config import settings

app = FastAPI(
    title="Whiteboard Visual Generator API",
    description="AI-powered visual storyboard generator with web interface",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
templates = Jinja2Templates(directory="templates")

# Initialize services
gemini_service = GeminiService()
visual_service = VisualService()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the enhanced home page with image viewing capability"""
    return templates.TemplateResponse("visual_index.html", {"request": request})

@app.post("/api/create-visuals", response_model=VisualResponse)
def create_visuals(req: VisualRequest):
    """Create visual storyboard with enhanced error handling"""
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
async def get_image(filename: str):
    """Serve generated images with proper headers"""
    full_path = os.path.join(settings.IMAGES_DIR, filename)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        full_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"}
    )

@app.get("/api/styles")
async def get_visual_styles():
    """Get available visual styles"""
    return {
        "styles": [
            {"value": "whiteboard", "label": "Whiteboard"},
            {"value": "sketch", "label": "Sketch"},
            {"value": "infographic", "label": "Infographic"},
            {"value": "minimal", "label": "Minimal"}
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "visual_generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
