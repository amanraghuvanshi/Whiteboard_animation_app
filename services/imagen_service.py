# services/imagen_service.py
import asyncio
import base64
import io, os
import time
from typing import Optional, Tuple
from google.cloud import aiplatform
from google.auth import default
import httpx
from PIL import Image
import logging

from utils.config import settings
from models.schemas import VisualPanel, VisualStyle, ImageGenerationStatus

logger = logging.getLogger(__name__)

class ImagenService:
    def __init__(self):
        logger.info("Initializing Imagen v4 service...")
        try:
            # Initialize Google Cloud AI Platform
            aiplatform.init(
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
            
            # Set up authentication
            self.credentials, self.project_id = default()
            logger.info(f"Successfully initialized Imagen service for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Imagen service: {e}")
            raise Exception(f"Imagen initialization failed: {e}")
    
    async def generate_panel_image(self, panel: VisualPanel, style: VisualStyle, 
                                 task_id: str) -> Tuple[Optional[str], str]:
        """
        Generate image using Google Cloud Imagen v4
        Returns: (image_path, status_message)
        """
        logger.info(f"Starting image generation for panel {panel.sequence} (Task: {task_id})")
        
        try:
            # Update panel status
            panel.image_generation_status = ImageGenerationStatus.GENERATING
            
            # Create optimized prompt for Imagen v4
            imagen_prompt = self._create_imagen_prompt(panel, style)
            panel.image_generation_prompt = imagen_prompt
            
            logger.debug(f"Generated prompt for panel {panel.sequence}: {imagen_prompt}")
            
            # Generate image with retry logic
            image_data = await self._generate_with_retry(imagen_prompt, panel.sequence)
            
            if image_data:
                # Save image
                image_path = await self._save_image(image_data, panel.sequence, task_id)
                panel.image_generation_status = ImageGenerationStatus.COMPLETED
                
                logger.info(f"Successfully generated image for panel {panel.sequence}: {image_path}")
                return image_path, "Image generated successfully"
            else:
                panel.image_generation_status = ImageGenerationStatus.FAILED
                logger.error(f"Failed to generate image for panel {panel.sequence}")
                return None, "Image generation failed"
                
        except Exception as e:
            panel.image_generation_status = ImageGenerationStatus.FAILED
            error_msg = f"Error generating image for panel {panel.sequence}: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def _create_imagen_prompt(self, panel: VisualPanel, style: VisualStyle) -> str:
        """Create optimized prompt for Imagen v4"""
        
        style_instructions = {
            VisualStyle.WHITEBOARD: "Clean educational whiteboard drawing style, black markers on white background, simple line art, clear diagrams",
            VisualStyle.SKETCH: "Hand-drawn pencil sketch style, artistic strokes, educational illustration, black and white",
            VisualStyle.INFOGRAPHIC: "Modern clean infographic style, flat design, bright colors, professional business illustration",
            VisualStyle.MINIMAL: "Minimalist line art, simple geometric shapes, clean vector style, monochromatic"
        }
        
        # Build comprehensive prompt
        prompt = f"""
{style_instructions[style]}

Subject: {panel.title}
Description: {panel.description}

Visual elements to include: {', '.join(panel.visual_elements)}

Additional requirements:
- Educational and professional appearance
- High contrast for readability
- Clear visual hierarchy
- Suitable for presentations and learning materials
- 16:9 aspect ratio
- Clean composition with good use of white space
- No text or labels in the image
- Focus on visual storytelling
"""
        
        logger.debug(f"Created Imagen prompt: {prompt[:200]}...")
        return prompt.strip()
    
    async def _generate_with_retry(self, prompt: str, panel_sequence: int) -> Optional[bytes]:
        """Generate image with retry logic"""
        
        for attempt in range(settings.MAX_IMAGE_RETRIES):
            try:
                logger.info(f"Image generation attempt {attempt + 1}/{settings.MAX_IMAGE_RETRIES} for panel {panel_sequence}")
                
                # Call Imagen v4 API
                image_data = await self._call_imagen_api(prompt)
                
                if image_data:
                    logger.info(f"Successfully generated image on attempt {attempt + 1}")
                    return image_data
                else:
                    logger.warning(f"Attempt {attempt + 1} returned no data")
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < settings.MAX_IMAGE_RETRIES - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("All retry attempts exhausted")
        
        return None
    
    async def _call_imagen_api(self, prompt: str) -> Optional[bytes]:
        """Make actual API call to Imagen v4"""
        
        try:
            # Get access token
            credentials, _ = default()
            credentials.refresh(httpx.Request())
            access_token = credentials.token
            
            # Prepare API request
            url = f"https://{settings.GOOGLE_CLOUD_LOCATION}-aiplatform.googleapis.com/v1/projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.GOOGLE_CLOUD_LOCATION}/publishers/google/models/{settings.IMAGEN_MODEL}:predict"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Request payload for Imagen v4
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "16:9",
                    "safetyFilterLevel": "block_some",
                    "personGeneration": "dont_allow"
                }
            }
            
            logger.debug(f"Making API request to: {url}")
            logger.debug(f"Payload: {payload}")
            
            # Make async HTTP request
            async with httpx.AsyncClient(timeout=settings.IMAGE_GENERATION_TIMEOUT) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                logger.debug(f"API response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"API response: {str(result)[:200]}...")
                    
                    if "predictions" in result and len(result["predictions"]) > 0:
                        # Extract base64 image data
                        image_b64 = result["predictions"][0].get("bytesBase64Encoded")
                        if image_b64:
                            image_data = base64.b64decode(image_b64)
                            logger.info(f"Successfully decoded image data ({len(image_data)} bytes)")
                            return image_data
                        else:
                            logger.error("No image data in API response")
                    else:
                        logger.error("No predictions in API response")
                else:
                    error_text = response.text
                    logger.error(f"API request failed: {response.status_code} - {error_text}")
                    
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise
        
        return None
    
    async def _save_image(self, image_data: bytes, panel_sequence: int, task_id: str) -> str:
        """Save generated image to disk"""
        
        try:
            # Load image and verify
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Image loaded: {image.size} pixels, mode: {image.mode}")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                logger.debug("Converted image to RGB mode")
            
            # Resize if needed (maintain aspect ratio)
            if image.width > 1200 or image.height > 800:
                image.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                logger.debug(f"Resized image to: {image.size}")
            
            # Save to file
            filename = f"{task_id}_panel_{panel_sequence}_imagen.png"
            filepath = os.path.join(settings.IMAGES_DIR, filename)
            
            image.save(filepath, "PNG", quality=95, optimize=True)
            logger.info(f"Image saved to: {filepath}")
            
            # Verify file was created
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"File verified: {filepath} ({file_size} bytes)")
                return filepath
            else:
                raise Exception("File was not created successfully")
                
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            raise
