# Whiteboard Visual Storyboard Generator - Complete API Documentation

A comprehensive FastAPI application that generates static visual storyboards from natural language prompts using Google Gemini AI and Pillow for image rendering.

## 🚀 Quick Start

```bash
git clone 
cd whiteboard_visual_app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Start the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### Base URL
```
http://localhost:8000
```

## 🎨 Visual Generation Endpoints

### 1. Create Visual Storyboard

**Endpoint:** `POST /api/create-visuals`

**Description:** Generate a multi-panel visual storyboard from a text prompt using AI.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "string (min 10 characters)",
  "style": "whiteboard | sketch | infographic | minimal",
  "panels": "integer (1-9)"
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Description of what to visualize (minimum 10 characters) |
| `style` | enum | No | `"whiteboard"` | Visual style theme |
| `panels` | integer | No | `4` | Number of panels to generate (1-9) |

**Example Request:**
```json
{
  "prompt": "Explain the process of photosynthesis in plants step by step",
  "style": "whiteboard",
  "panels": 4
}
```

**Success Response (200):**
```json
{
  "panels": [
    {
      "sequence": 1,
      "title": "Light Absorption",
      "description": "Chloroplasts in plant leaves absorb sunlight energy",
      "visual_elements": [
        "sun rays",
        "leaf diagram",
        "chloroplast structure"
      ],
      "text_content": "Plants capture sunlight using chlorophyll in their leaves"
    },
    {
      "sequence": 2,
      "title": "Water Uptake",
      "description": "Roots absorb water and minerals from soil",
      "visual_elements": [
        "root system",
        "water molecules",
        "soil particles"
      ],
      "text_content": "Roots take in water and nutrients from the ground"
    }
  ],
  "image_paths": [
    "/outputs/images/uuid_panel_1.png",
    "/outputs/images/uuid_panel_2.png"
  ],
  "message": "Successfully generated 4 panels and 4 images"
}
```

**Error Response (400):**
```json
{
  "detail": "Prompt must be at least 10 characters long"
}
```

**Error Response (500):**
```json
{
  "detail": "Internal server error: Failed to generate panels from Gemini"
}
```

### 2. Get Available Styles

**Endpoint:** `GET /api/styles`

**Description:** Retrieve all available visual styles for storyboard generation.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/styles"
```

**Success Response (200):**
```json
{
  "styles": [
    {
      "value": "whiteboard",
      "label": "Whiteboard"
    },
    {
      "value": "sketch",
      "label": "Sketch"
    },
    {
      "value": "infographic",
      "label": "Infographic"
    },
    {
      "value": "minimal",
      "label": "Minimal"
    }
  ]
}
```

## 🖼️ Image Serving Endpoints

### 3. Get Generated Image

**Endpoint:** `GET /outputs/images/{filename}`

**Description:** Serve generated panel images with proper caching headers.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filename` | string | Yes | Name of the generated image file |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/outputs/images/abc123_panel_1.png"
```

**Success Response (200):**
- Returns the PNG image file
- Headers: `Content-Type: image/png`, `Cache-Control: public, max-age=3600`

**Error Response (404):**
```json
{
  "detail": "Image not found"
}
```

## 🌐 Web Interface Endpoints

### 4. Home Page

**Endpoint:** `GET /`

**Description:** Serves the interactive web interface for creating and viewing storyboards.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/"
```

**Success Response (200):**
Returns HTML page with:
- Form for prompt input and style selection
- Real-time progress tracking
- Image gallery with modal viewer
- Download functionality for each panel

### 5. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API service is running properly.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Success Response (200):**
```json
{
  "status": "healthy",
  "service": "visual_generator"
}
```

## 📋 Complete cURL Examples

### Generate a Business Process Storyboard
```bash
curl -X POST "http://localhost:8000/api/create-visuals" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show the steps to start a small business from idea to launch",
    "style": "infographic",
    "panels": 6
  }'
```

### Generate a Science Explanation
```bash
curl -X POST "http://localhost:8000/api/create-visuals" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain how the water cycle works in nature",
    "style": "whiteboard",
    "panels": 4
  }'
```

### Generate a Tutorial Storyboard
```bash
curl -X POST "http://localhost:8000/api/create-visuals" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How to bake chocolate chip cookies from scratch",
    "style": "sketch",
    "panels": 5
  }'
```

## 🔧 Response Data Models

### VisualPanel Model
```json
{
  "sequence": "integer - Panel order number",
  "title": "string - Brief panel title",
  "description": "string - Detailed description of visual content",
  "visual_elements": ["array of strings - Specific elements to include"],
  "text_content": "string - Main text content for the panel"
}
```

### VisualResponse Model
```json
{
  "panels": ["array of VisualPanel objects"],
  "image_paths": ["array of strings - URLs to generated images"],
  "message": "string - Status message"
}
```

## ⚠️ Error Handling

### Common Error Scenarios

**Validation Errors (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "ensure this value has at least 10 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Gemini API Errors (500):**
```json
{
  "detail": "Internal server error: Gemini API key not configured"
}
```

**Image Generation Errors (500):**
```json
{
  "detail": "Internal server error: Failed to create panel images"
}
```

## 🎯 Usage Patterns

### Educational Content
```json
{
  "prompt": "Explain the life cycle of a butterfly with detailed transformations",
  "style": "whiteboard",
  "panels": 4
}
```

### Business Processes
```json
{
  "prompt": "Customer journey from awareness to purchase in e-commerce",
  "style": "infographic",
  "panels": 6
}
```

### Technical Tutorials
```json
{
  "prompt": "How to set up a REST API with authentication and database",
  "style": "minimal",
  "panels": 8
}
```

## 🔐 Authentication

Currently, no authentication is required for API access. For production deployment, consider implementing:
- API key authentication
- Rate limiting
- CORS configuration

## 📊 Rate Limits

No rate limits are currently enforced. For production use, consider implementing:
- Request rate limiting per IP
- Daily quota limits
- Concurrent request limits

## 🐛 Troubleshooting

### Common Issues

1. **Empty panels array returned:**
   - Check Gemini API key configuration
   - Verify prompt meets minimum length requirement
   - Check server logs for JSON parsing errors

2. **No images generated:**
   - Ensure `outputs/images/` directory exists
   - Check file system permissions
   - Verify Pillow dependencies are installed

3. **500 Internal Server Error:**
   - Check Gemini API key validity
   - Monitor server logs for detailed error messages
   - Verify all required environment variables are set

### Debug Commands

Check service health:
```bash
curl -X GET "http://localhost:8000/health"
```

Test with minimal request:
```bash
curl -X POST "http://localhost:8000/api/create-visuals" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Simple test prompt", "panels": 1}'
```

## 📈 Performance Considerations

- **Synchronous Processing:** All requests are processed synchronously
- **Image Generation Time:** Typically 5-15 seconds depending on panel count
- **File Storage:** Images are stored locally in `outputs/images/`
- **Memory Usage:** Moderate memory usage for image generation

## 🚀 Production Deployment

For production deployment, consider:

1. **Environment Configuration:**
   ```env
   GEMINI_API_KEY=production_key
   OUTPUT_DIR=/app/outputs
   IMAGES_DIR=/app/outputs/images
   ```

2. **Docker Deployment:**
   ```dockerfile
   FROM python:3.11-slim
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Reverse Proxy Configuration (nginx):**
   ```nginx
   location /api/ {
       proxy_pass http://localhost:8000/api/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```
