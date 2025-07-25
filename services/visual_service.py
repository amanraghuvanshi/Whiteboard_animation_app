from PIL import Image, ImageDraw, ImageFont
import os
from models.schemas import VisualPanel, VisualStyle
from utils.config import settings

class VisualService:
    def create_panels(self, panels, style, task_id):
        print(f"Creating panels for task: {task_id}")
        print(f"Number of panels received: {len(panels)}")
        print(f"Output directory: {settings.IMAGES_DIR}")
        
        # Ensure output directory exists
        os.makedirs(settings.IMAGES_DIR, exist_ok=True)
        
        if not panels:
            print("Warning: No panels provided to create_panels")
            return []
        
        paths = []
        
        for i, panel in enumerate(panels):
            print(f"Creating panel {i+1}: {panel.title}")
            
            try:
                # Create image with better sizing and styling
                img = Image.new("RGB", (1200, 800), "white")
                draw = ImageDraw.Draw(img)
                
                # Try to load a font, fallback to default if not available
                try:
                    title_font = ImageFont.truetype("arial.ttf", 36)
                    text_font = ImageFont.truetype("arial.ttf", 24)
                except:
                    title_font = ImageFont.load_default()
                    text_font = ImageFont.load_default()
                
                # Draw title
                draw.text((50, 50), panel.title, fill="black", font=title_font)
                
                # Draw description
                description_lines = self._wrap_text(panel.description, 80)
                y_pos = 120
                for line in description_lines:
                    draw.text((50, y_pos), line, fill="gray", font=text_font)
                    y_pos += 30
                
                # Draw text content
                content_lines = self._wrap_text(panel.text_content, 80)
                y_pos += 50
                for line in content_lines:
                    draw.text((50, y_pos), line, fill="black", font=text_font)
                    y_pos += 30
                
                # Draw visual elements list
                y_pos += 50
                draw.text((50, y_pos), "Visual Elements:", fill="blue", font=text_font)
                y_pos += 30
                for element in panel.visual_elements:
                    draw.text((70, y_pos), f"-  {element}", fill="blue", font=text_font)
                    y_pos += 25
                
                # Save image
                img_filename = f"{task_id}_panel_{panel.sequence}.png"
                img_path = os.path.join(settings.IMAGES_DIR, img_filename)
                
                img.save(img_path, quality=95)
                print(f"Saved image: {img_path}")
                
                # Verify file was created
                if os.path.exists(img_path):
                    paths.append(img_path)
                    print(f"Confirmed file exists: {img_path}")
                else:
                    print(f"Error: File was not created: {img_path}")
                    
            except Exception as e:
                print(f"Error creating panel {i+1}: {e}")
                continue
        
        print(f"Successfully created {len(paths)} panel images")
        return paths
    
    def _wrap_text(self, text, width):
        """Simple text wrapping function"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
