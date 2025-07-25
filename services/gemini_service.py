import google.generativeai as genai
import json
import logging
from utils.config import settings
from models.schemas import VisualPanel, VisualStyle

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def extract_json_from_response(self, raw_text: str) -> str:
        """Extract JSON content from Gemini response, handling markdown formatting"""
        print(f"Raw Gemini response: {raw_text[:500]}...")  # Debug log

        # Handle markdown code blocks
        if "```json" in raw_text: # Corrected line: added closing backtick
            start = raw_text.find("```json") + 7
            end = raw_text.find("```", start) # Start searching for "```" from after "```json"
            if end != -1:
                return raw_text[start:end].strip()
        elif "```" in raw_text:
            # Handle generic code blocks
            lines = raw_text.split('\n')
            json_lines = []
            in_code_block = False

            for line in lines:
                if line.strip() == "```":
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    json_lines.append(line)

            return '\n'.join(json_lines)

        # If no code blocks, return cleaned text
        return raw_text.strip()

    def generate_visual_storyboard(self, prompt, style, panels):
        system_prompt = f"""
        Create exactly {panels} panels for a {style.value} storyboard explaining: {prompt}
        
        You MUST return a valid JSON array with exactly this structure:
        [
          {{
            "sequence": 1,
            "title": "Short Panel Title",
            "description": "What should be visually depicted",
            "visual_elements": ["element1", "element2", "element3"],
            "text_content": "Main text for this panel"
          }}
        ]
        
        Requirements:
        - Return ONLY the JSON array, no additional text
        - Each panel must have all 5 fields: sequence, title, description, visual_elements, text_content
        - visual_elements must be an array of strings
        - Make sure the JSON is valid and complete
        """
        
        try:
            resp = self.model.generate_content(system_prompt)
            raw_text = resp.text
            
            # Log the raw response for debugging
            print(f"Gemini raw response: {raw_text}")
            
            # Extract and clean JSON
            json_str = self.extract_json_from_response(raw_text)
            print(f"Extracted JSON string: {json_str}")
            
            # Parse JSON
            try:
                panels_data = json.loads(json_str)
                print(f"Parsed panels data: {panels_data}")
                
                if not isinstance(panels_data, list):
                    print("Error: Panels data is not a list")
                    return self._create_fallback_panels(prompt, panels)
                
                # Validate and create VisualPanel objects
                visual_panels = []
                for panel_dict in panels_data:
                    try:
                        panel = VisualPanel(**panel_dict)
                        visual_panels.append(panel)
                        print(f"Created panel: {panel.title}")
                    except Exception as e:
                        print(f"Error creating panel: {e}")
                        continue
                
                if not visual_panels:
                    print("No valid panels created, using fallback")
                    return self._create_fallback_panels(prompt, panels)
                
                return visual_panels
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Problematic JSON string: {json_str}")
                return self._create_fallback_panels(prompt, panels)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._create_fallback_panels(prompt, panels)

    def _create_fallback_panels(self, prompt: str, num_panels: int):
        """Create simple fallback panels when Gemini fails"""
        print(f"Creating {num_panels} fallback panels for: {prompt}")
        
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
                description=f"Visual representation of: {panel_text}",
                visual_elements=["text", "simple diagram", "arrow"],
                text_content=panel_text
            )
            panels.append(panel)
            
        return panels
