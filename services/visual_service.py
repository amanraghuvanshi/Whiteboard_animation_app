from PIL import Image, ImageDraw, ImageFont
import os
from models.schemas import VisualPanel, VisualStyle
from utils.config import settings

class VisualService:
    def create_panels(self, panels, style, task_id):
        paths = []
        for panel in panels:
            img = Image.new("RGB", (800, 600), "white")
            draw = ImageDraw.Draw(img)
            draw.text((40, 40), panel.title, fill="black")
            draw.text((40, 120), panel.text_content, fill="gray")
            img_path = os.path.join(settings.IMAGES_DIR, f"{task_id}_panel_{panel.sequence}.png")
            img.save(img_path)
            paths.append(img_path)
        return paths
