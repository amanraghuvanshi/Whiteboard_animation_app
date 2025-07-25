from PIL import Image, ImageDraw, ImageFont
import os
import math
from models.schemas import VisualPanel, VisualStyle
from utils.config import settings

class VisualService:
    def __init__(self):
        self.canvas_width = 1200
        self.canvas_height = 900
        
    def create_panels(self, panels, style, task_id):
        print(f"Creating enhanced visual panels for task: {task_id}")
        
        os.makedirs(settings.IMAGES_DIR, exist_ok=True)
        
        if not panels:
            return []
        
        paths = []
        
        for i, panel in enumerate(panels):
            try:
                img_path = self._create_enhanced_panel(panel, style, task_id)
                if img_path:
                    paths.append(img_path)
            except Exception as e:
                print(f"Error creating panel {i+1}: {e}")
                continue
        
        return paths
    
    def _create_enhanced_panel(self, panel: VisualPanel, style: VisualStyle, task_id: str):
        """Create a panel with actual visual elements"""
        
        # Create canvas
        img = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            text_font = ImageFont.truetype("arial.ttf", 24)
            element_font = ImageFont.truetype("arial.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default() 
            element_font = ImageFont.load_default()
        
        # Style configuration
        colors = self._get_style_colors(style)
        
        # Draw background elements based on style
        self._draw_background(draw, style, colors)
        
        # Title area (top 15% of canvas)
        title_y = 50
        self._draw_title(draw, panel.title, title_font, colors, title_y)
        
        # Main visual area (middle 60% of canvas) 
        visual_start_y = 150
        visual_height = 500
        self._draw_visual_elements(draw, panel.visual_elements, colors, 
                                 visual_start_y, visual_height)
        
        # Text content area (bottom 25% of canvas)
        text_start_y = 700
        self._draw_text_content(draw, panel.text_content, text_font, colors, text_start_y)
        
        # Panel number badge
        self._draw_panel_number(draw, panel.sequence, colors)
        
        # Save image
        img_filename = f"{task_id}_panel_{panel.sequence}.png"
        img_path = os.path.join(settings.IMAGES_DIR, img_filename)
        img.save(img_path, quality=95)
        
        return img_path
    
    def _get_style_colors(self, style: VisualStyle):
        """Define color schemes for different styles"""
        color_schemes = {
            VisualStyle.WHITEBOARD: {
                'bg': 'white', 'text': 'black', 'accent': '#2196F3', 
                'secondary': '#4CAF50', 'border': '#666666'
            },
            VisualStyle.SKETCH: {
                'bg': '#F5F5DC', 'text': '#333333', 'accent': '#8B4513',
                'secondary': '#CD853F', 'border': '#A0522D' 
            },
            VisualStyle.INFOGRAPHIC: {
                'bg': 'white', 'text': '#2C3E50', 'accent': '#3498DB',
                'secondary': '#E74C3C', 'border': '#34495E'
            },
            VisualStyle.MINIMAL: {
                'bg': 'white', 'text': '#444444', 'accent': '#666666',
                'secondary': '#999999', 'border': '#CCCCCC'
            }
        }
        return color_schemes.get(style, color_schemes[VisualStyle.WHITEBOARD])
    
    def _draw_background(self, draw, style, colors):
        """Draw style-specific background elements"""
        if style == VisualStyle.WHITEBOARD:
            # Add subtle grid lines
            for x in range(0, self.canvas_width, 100):
                draw.line([(x, 0), (x, self.canvas_height)], fill='#F0F0F0', width=1)
            for y in range(0, self.canvas_height, 100):
                draw.line([(0, y), (self.canvas_width, y)], fill='#F0F0F0', width=1)
                
        elif style == VisualStyle.SKETCH:
            # Add paper texture effect with dots
            for x in range(50, self.canvas_width, 150):
                for y in range(50, self.canvas_height, 150):
                    draw.ellipse([x-2, y-2, x+2, y+2], fill='#E0E0E0')
    
    def _draw_title(self, draw, title, font, colors, y_pos):
        """Draw the panel title with underline"""
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.canvas_width - title_width) // 2
        
        # Draw title
        draw.text((title_x, y_pos), title, fill=colors['text'], font=font)
        
        # Draw underline
        underline_y = y_pos + title_bbox[3] + 10
        draw.line([(title_x, underline_y), (title_x + title_width, underline_y)], 
                 fill=colors['accent'], width=3)
    
    def _draw_visual_elements(self, draw, visual_elements, colors, start_y, height):
        """Draw actual visual representations of the elements"""
        if not visual_elements:
            return
            
        # Calculate layout for visual elements
        elements_per_row = min(3, len(visual_elements))
        rows = math.ceil(len(visual_elements) / elements_per_row)
        
        element_width = 300
        element_height = height // max(rows, 1)
        
        for i, element in enumerate(visual_elements[:9]):  # Limit to 9 elements
            row = i // elements_per_row
            col = i % elements_per_row
            
            # Calculate position
            total_width = elements_per_row * element_width
            start_x = (self.canvas_width - total_width) // 2
            
            x = start_x + col * element_width + element_width // 2
            y = start_y + row * element_height + element_height // 2
            
            # Draw the visual element
            self._draw_single_visual_element(draw, element, x, y, colors, element_width//3)
            
            # Add label
            label_y = y + element_height//3 + 20
            self._draw_centered_text(draw, element, x, label_y, colors['text'])
    
    def _draw_single_visual_element(self, draw, element, center_x, center_y, colors, size):
        """Draw individual visual elements based on description"""
        element_lower = element.lower()
        
        if any(word in element_lower for word in ['arrow', 'direction', 'flow', 'point']):
            self._draw_arrow(draw, center_x, center_y, colors['accent'], size)
            
        elif any(word in element_lower for word in ['circle', 'round', 'cycle', 'wheel']):
            self._draw_circle(draw, center_x, center_y, colors['accent'], size)
            
        elif any(word in element_lower for word in ['square', 'box', 'rectangle', 'block']):
            self._draw_rectangle(draw, center_x, center_y, colors['accent'], size)
            
        elif any(word in element_lower for word in ['triangle', 'mountain', 'peak']):
            self._draw_triangle(draw, center_x, center_y, colors['accent'], size)
            
        elif any(word in element_lower for word in ['star', 'sparkle']):
            self._draw_star(draw, center_x, center_y, colors['accent'], size)
            
        elif any(word in element_lower for word in ['line', 'connection', 'link']):
            self._draw_line(draw, center_x, center_y, colors['accent'], size)
            
        elif any(word in element_lower for word in ['sun', 'light', 'ray']):
            self._draw_sun(draw, center_x, center_y, colors['secondary'], size)
            
        elif any(word in element_lower for word in ['tree', 'plant', 'leaf']):
            self._draw_tree(draw, center_x, center_y, colors['secondary'], size)
            
        elif any(word in element_lower for word in ['house', 'building', 'home']):
            self._draw_house(draw, center_x, center_y, colors['accent'], size)
            
        elif any(word in element_lower for word in ['person', 'human', 'figure', 'stick']):
            self._draw_stick_figure(draw, center_x, center_y, colors['text'], size)
            
        elif any(word in element_lower for word in ['water', 'wave', 'drop']):
            self._draw_water_drop(draw, center_x, center_y, colors['accent'], size)
            
        else:
            # Default: simple geometric shape
            self._draw_default_shape(draw, center_x, center_y, colors['accent'], size)
    
    def _draw_arrow(self, draw, x, y, color, size):
        """Draw an arrow"""
        points = [
            (x - size, y),
            (x + size//2, y),
            (x + size//2, y - size//3),
            (x + size, y),
            (x + size//2, y + size//3),
            (x + size//2, y)
        ]
        draw.polygon(points, fill=color, outline=color)
    
    def _draw_circle(self, draw, x, y, color, size):
        """Draw a circle"""
        draw.ellipse([x-size, y-size, x+size, y+size], outline=color, width=4)
    
    def _draw_rectangle(self, draw, x, y, color, size):
        """Draw a rectangle"""
        draw.rectangle([x-size, y-size//2, x+size, y+size//2], outline=color, width=4)
    
    def _draw_triangle(self, draw, x, y, color, size):
        """Draw a triangle"""
        points = [(x, y-size), (x-size, y+size), (x+size, y+size)]
        draw.polygon(points, outline=color, width=4)
    
    def _draw_star(self, draw, x, y, color, size):
        """Draw a 5-pointed star"""
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = size if i % 2 == 0 else size // 2
            px = x + radius * math.cos(angle - math.pi/2)
            py = y + radius * math.sin(angle - math.pi/2)
            points.append((px, py))
        draw.polygon(points, outline=color, width=3)
    
    def _draw_line(self, draw, x, y, color, size):
        """Draw a simple line"""
        draw.line([(x-size, y), (x+size, y)], fill=color, width=4)
    
    def _draw_sun(self, draw, x, y, color, size):
        """Draw a sun with rays"""
        # Central circle
        draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                    fill=color, outline=color)
        # Rays
        for i in range(8):
            angle = i * math.pi / 4
            x1 = x + (size//2 + 10) * math.cos(angle)
            y1 = y + (size//2 + 10) * math.sin(angle)
            x2 = x + (size + 20) * math.cos(angle)
            y2 = y + (size + 20) * math.sin(angle)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
    
    def _draw_tree(self, draw, x, y, color, size):
        """Draw a simple tree"""
        # Trunk
        trunk_width = size // 6
        trunk_height = size // 2
        draw.rectangle([x-trunk_width, y, x+trunk_width, y+trunk_height], 
                      fill='#8B4513', outline='#8B4513')
        # Leaves (circle)
        draw.ellipse([x-size//2, y-size, x+size//2, y], fill=color, outline=color)
    
    def _draw_house(self, draw, x, y, color, size):
        """Draw a simple house"""
        # Base
        draw.rectangle([x-size, y, x+size, y+size], outline=color, width=3)
        # Roof
        roof_points = [(x-size, y), (x, y-size//2), (x+size, y)]
        draw.polygon(roof_points, outline=color, width=3)
        # Door
        door_width = size // 3
        draw.rectangle([x-door_width//2, y+size//2, x+door_width//2, y+size], 
                      outline=color, width=2)
    
    def _draw_stick_figure(self, draw, x, y, color, size):
        """Draw a stick figure"""
        # Head
        head_size = size // 4
        draw.ellipse([x-head_size, y-size, x+head_size, y-size+2*head_size], 
                    outline=color, width=3)
        # Body
        draw.line([(x, y-size+2*head_size), (x, y+size//2)], fill=color, width=3)
        # Arms
        draw.line([(x-size//2, y-size//2), (x+size//2, y-size//2)], fill=color, width=3)
        # Legs
        draw.line([(x, y+size//2), (x-size//3, y+size)], fill=color, width=3)
        draw.line([(x, y+size//2), (x+size//3, y+size)], fill=color, width=3)
    
    def _draw_water_drop(self, draw, x, y, color, size):
        """Draw a water drop"""
        # Teardrop shape using polygon approximation
        points = []
        for i in range(20):
            angle = 2 * math.pi * i / 20
            if angle < math.pi:
                radius = size * math.sin(angle)
            else:
                radius = size * 0.3 * math.sin(angle)
            px = x + radius * math.cos(angle + math.pi/2)
            py = y + size * math.cos(angle/2)
            points.append((px, py))
        draw.polygon(points, fill=color, outline=color)
    
    def _draw_default_shape(self, draw, x, y, color, size):
        """Draw default shape when element type is unclear"""
        # Diamond shape
        points = [(x, y-size), (x+size, y), (x, y+size), (x-size, y)]
        draw.polygon(points, outline=color, width=4)
    
    def _draw_text_content(self, draw, text, font, colors, start_y):
        """Draw wrapped text content"""
        wrapped_lines = self._wrap_text(text, 80)
        line_height = 30
        
        for i, line in enumerate(wrapped_lines[:5]):  # Limit to 5 lines
            y = start_y + i * line_height
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            x = (self.canvas_width - text_width) // 2
            draw.text((x, y), line, fill=colors['text'], font=font)
    
    def _draw_panel_number(self, draw, sequence, colors):
        """Draw panel sequence number in corner"""
        circle_size = 40
        x = self.canvas_width - circle_size - 20
        y = 20
        
        # Circle background
        draw.ellipse([x, y, x + circle_size, y + circle_size], 
                    fill=colors['accent'], outline=colors['accent'])
        
        # Number text
        number_text = str(sequence)
        text_bbox = draw.textbbox((0, 0), number_text)
        text_x = x + (circle_size - (text_bbox[2] - text_bbox[0])) // 2
        text_y = y + (circle_size - (text_bbox[3] - text_bbox[1])) // 2
        draw.text((text_x, text_y), number_text, fill='white')
    
    def _draw_centered_text(self, draw, text, x, y, color):
        """Draw text centered at position"""
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = x - text_width // 2
        draw.text((text_x, y), text, fill=color)
    
    def _wrap_text(self, text, width):
        """Wrap text to specified width"""
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
