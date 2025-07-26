# services/gemini_service.py
import google.generativeai as genai
import json
import asyncio
import logging
from typing import List
from utils.config import settings
from models.schemas import VisualPanel, VisualStyle, ImageGenerationStatus

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        logger.info("Initializing Gemini service...")
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Successfully initialized Gemini service")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise

    def extract_json_from_response(self, raw_text: str) -> str:
        """Extract JSON content from Gemini response"""
        logger.debug(f"Extracting JSON from response: {raw_text[:100]}...")
        
        if "```":
            start = raw_text.find("```json") + 7
            end = raw_text.find("```")
            if end != -1:
                extracted = raw_text[start:end].strip()
                logger.debug(f"Extracted JSON: {extracted[:100]}...")
                return extracted
        elif "```" in raw_text:
            lines = raw_text.split('\n')
            json_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    json_lines.append(line)
            
            extracted = '\n'.join(json_lines)
            logger.debug(f"Extracted from code block: {extracted[:100]}...")
            return extracted
        
        # Return cleaned text
        cleaned = raw_text.strip("`\n ")
        logger.debug(f"Cleaned text: {cleaned[:100]}...")
        return cleaned

    async def generate_visual_storyboard(self, prompt: str, style: VisualStyle, panels: int) -> List[VisualPanel]:
        """Generate storyboard panels optimized for Imagen v4"""
        
        logger.info(f"Generating storyboard: {panels} panels, style: {style.value}")
        logger.debug(f"User prompt: {prompt}")
        
        system_prompt = f"""
        Create exactly {panels} panels for a {style.value} visual storyboard explaining: {prompt}
        
        Each panel should be optimized for AI image generation with detailed visual descriptions.
        
        Return ONLY a valid JSON array with this exact structure:
        [
          {{
            "sequence": 1,
            "title": "Clear Panel Title (max 8 words)",
            "description": "Detailed visual description for AI image generation (2-3 sentences explaining exactly what should be shown visually)",
            "visual_elements": ["specific element 1", "specific element 2", "specific element 3"],
            "text_content": "Concise educational text for this panel (1-2 sentences)"
          }}
        ]
        
        Important guidelines:
        - Make descriptions very specific and visual (what objects, colors, composition)
        - Visual elements should be concrete things that can be drawn/illustrated
        - Optimize descriptions for AI image generation
        - Ensure logical flow between panels
        - Each panel must have all required fields
        - Keep content educational and clear
        """
        
        try:
            logger.debug("Calling Gemini API...")
            response = await asyncio.to_thread(
                self.model.generate_content, 
                system_prompt
            )
            
            raw_text = response.text
            logger.debug(f"Gemini raw response: {raw_text}")
            
            # Extract and parse JSON
            json_str = self.extract_json_from_response(raw_text)
            logger.debug(f"Extracted JSON string: {json_str}")
            
            try:
                panels_data = json.loads(json_str)
                logger.info(f"Successfully parsed {len(panels_data)} panels from JSON")
                
                if not isinstance(panels_data, list):
                    logger.error("Parsed data is not a list")
                    return self._create_fallback_panels(prompt, panels)
                
                # Create VisualPanel objects
                visual_panels = []
                for i, panel_dict in enumerate(panels_data):
                    try:
                        # Add image generation status
                        panel_dict["image_generation_status"] = ImageGenerationStatus.PENDING
                        
                        panel = VisualPanel(**panel_dict)
                        visual_panels.append(panel)
                        logger.debug(f"Created panel {i+1}: {panel.title}")
                        
                    except Exception as e:
                        logger.error(f"Error creating panel {i+1}: {e}")
                        continue
                
                if not visual_panels:
                    logger.warning("No valid panels created, using fallback")
                    return self._create_fallback_panels(prompt, panels)
                
                logger.info(f"Successfully created {len(visual_panels)} visual panels")
                return visual_panels
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.debug(f"Problematic JSON: {json_str}")
                return self._create_fallback_panels(prompt, panels)
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._create_fallback_panels(prompt, panels)

    def _create_fallback_panels(self, prompt: str, num_panels: int) -> List[VisualPanel]:
        """Create fallback panels when Gemini fails"""
        logger.warning(f"Creating {num_panels} fallback panels for: {prompt}")
        
        panels = []
        words = prompt.split()
        words_per_panel = max(3, len(words) // num_panels)
        
        for i in range(num_panels):
            start_idx = i * words_per_panel
            end_idx = min((i + 1) * words_per_panel, len(words))
            panel_text = ' '.join(words[start_idx:end_idx])
            
            panel = VisualPanel(
                sequence=i + 1,
                title=f"Step {i + 1}",
                description=f"Visual illustration showing: {panel_text}. Include clear diagrams and educational elements.",
                visual_elements=["educational diagram", "clear illustration", "visual explanation"],
                text_content=panel_text,
                image_generation_status=ImageGenerationStatus.PENDING
            )
            panels.append(panel)
            logger.debug(f"Created fallback panel {i+1}")
            
        return panels
