import google.generativeai as genai
import json
from utils.config import settings
from models.schemas import VisualPanel, VisualStyle

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_visual_storyboard(self, prompt, style, panels):
        system_prompt = f"""
        Create a {panels}-panel {style.value} storyboard for: {prompt}
        Return JSON array as:
        {{
            "sequence": 1,
            "title": "...",
            "description": "...",
            "visual_elements": ["..."],
            "text_content": "..."
        }}"""
        resp = self.model.generate_content(system_prompt)
        json_str = resp.text
        return [VisualPanel(**panel) for panel in json.loads(json_str)]
