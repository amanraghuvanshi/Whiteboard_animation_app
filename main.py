# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uuid
import os
import logging

from models.schemas import VisualRequest, VisualResponse
from services.integrated_visual_service import IntegratedVisualService
from utils.config import settings

# Setup logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered Whiteboard Visual Generator with Imagen v4",
    description="Generate professional visual storyboards using Google Cloud Imagen v4",
    version="2.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
templates = Jinja2Templates(directory="templates")

# Initialize integrated service
try:
    visual_service = IntegratedVisualService()
    logger.info("Successfully initialized visual service")
except Exception as e:
    logger.error(f"Failed to initialize visual service: {e}")
    raise

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the enhanced home page"""
    logger.info("Serving home page")
    return templates.TemplateResponse("visual_index.html", {"request": request})

@app.post("/api/create-visuals", response_model=VisualResponse)
async def create_visuals(req: VisualRequest):
    """Create visual storyboard with Imagen v4"""
    logger.info(f"Received visual creation request: {req.prompt[:50]}...")
    logger.debug(f"Full request: {req}")
    
    try:
        task_id = str(uuid.uuid4())
        logger.info(f"Generated task ID: {task_id}")
        
        # Create storyboard with integrated service
        logger.info("Starting integrated storyboard creation...")
        panels, image_paths, stats = await visual_service.create_storyboard(
            req.prompt, req.style, req.panels, task_id
        )
        
        if not panels:
            logger.error("No panels were created")
            return VisualResponse(
                panels=[],
                image_paths=[],
                message="Failed to generate any panels",
                generation_stats=stats
            )
        
        # Convert file paths to URLs
        img_urls = [f"/outputs/images/{os.path.basename(p)}" for p in image_paths]
        logger.info(f"Generated {len(img_urls)} image URLs")
        
        # Create response
        response = VisualResponse(
            panels=panels,
            image_paths=img_urls,
            message=f"Successfully generated {len(panels)} panels with Imagen v4 and Gemini AI",
            generation_stats=stats
        )
        
        logger.info(f"Request completed successfully: {stats}")
        return response
        
    except Exception as e:
        error_msg = f"Visual creation failed: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.debug(traceback.format_exc())
        
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/outputs/images/{filename}")
async def get_image(filename: str):
    """Serve generated images"""
    logger.debug(f"Serving image: {filename}")
    
    full_path = os.path.join(settings.IMAGES_DIR, filename)
    
    if not os.path.exists(full_path):
        logger.error(f"Image not found: {full_path}")
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
            {"value": "whiteboard", "label": "Whiteboard", "description": "Clean educational whiteboard style"},
            {"value": "sketch", "label": "Sketch", "description": "Hand-drawn artistic sketch style"},
            {"value": "infographic", "label": "Infographic", "description": "Modern flat design infographic style"},
            {"value": "minimal", "label": "Minimal", "description": "Clean minimalist line art style"}
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    logger.info("Health check requested")
    
    health_status = {
        "status": "healthy",
        "service": "imagen_visual_generator",
        "version": "2.0.0",
        "features": {
            "imagen_v4": True,
            "gemini_ai": True,
            "fallback_generation": True
        }
    }
    
    # Test Google Cloud connection
    try:
        # This is a simple check - in production you might want more thorough testing
        import google.auth
        credentials, project_id = google.auth.default()
        health_status["google_cloud_project"] = project_id
        health_status["authentication"] = "valid"
    except Exception as e:
        logger.warning(f"Google Cloud auth check failed: {e}")
        health_status["authentication"] = "warning"
        health_status["auth_error"] = str(e)
    
    return health_status

@app.get("/api/debug/task/{task_id}")
async def debug_task_info(task_id: str):
    """Debug endpoint to check task-related files"""
    if not settings.DEBUG_MODE:
        raise HTTPException(status_code=404, detail="Debug mode not enabled")
    
    # Find files related to this task
    task_files = []
    if os.path.exists(settings.IMAGES_DIR):
        for filename in os.listdir(settings.IMAGES_DIR):
            if task_id in filename:
                filepath = os.path.join(settings.IMAGES_DIR, filename)
                file_info = {
                    "filename": filename,
                    "size": os.path.getsize(filepath),
                    "exists": os.path.exists(filepath)
                }
                task_files.append(file_info)
    
    return {
        "task_id": task_id,
        "files": task_files,
        "debug_mode": settings.DEBUG_MODE
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug" if settings.DEBUG_MODE else "info"
    )
