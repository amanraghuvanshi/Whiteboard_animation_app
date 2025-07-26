# services/hybrid_visual_service.py
from PIL import Image, ImageDraw, ImageFont
import io, os
from services.gemini_service import GeminiService

class HybridVisualService:
    def __init__(self):
        self.gemini_service = GeminiService()
        
    async def create_enhanced_panel(self, panel, style, task_id):
        """Create panel with AI-generated visual + text overlay"""
        
        # Generate base illustration with Gemini
        visual_prompt = self._create_visual_prompt(panel, style)
        ai_image_data = await self.gemini_service.generate_panel_image(
            visual_prompt, style
        )
        
        # Load AI-generated image
        base_image = Image.open(io.BytesIO(ai_image_data))
        base_image = base_image.resize((1200, 800))
        
        # Add text overlays and enhancements
        enhanced_image = self._add_text_overlays(base_image, panel, style)
        
        # Save final image
        img_path = os.path.join(settings.IMAGES_DIR, f"{task_id}_panel_{panel.sequence}.png")
        enhanced_image.save(img_path, quality=95)
        
        return img_path
    
    def _create_visual_prompt(self, panel, style):
        """Create optimized prompt for image generation"""
        return f"""
        Educational {style.value} illustration showing: {panel.description}
        
        Visual elements to include: {', '.join(panel.visual_elements)}
        
        Requirements:
        - Clean, professional educational style
        - Clear visual hierarchy
        - Appropriate for learning materials
        - Leave space at top and bottom for text overlays
        """
    
    def _add_text_overlays(self, base_image, panel, style):
        """Add title and text overlays to AI-generated image"""
        draw = ImageDraw.Draw(base_image)
        
        # Add semi-transparent text backgrounds
        self._add_text_background(draw, base_image.size)
        
        # Add title and content
        self._draw_title_overlay(draw, panel.title, base_image.size)
        self._draw_content_overlay(draw, panel.text_content, base_image.size)
        
        return base_image
