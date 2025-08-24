"""
Image Analysis Module for LabAcc Copilot

Provides image understanding capabilities using vision LLMs (GLM-4.5V).
Can be used both as an internal function and as a React agent tool.
"""

import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from PIL import Image
import io

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

# Supported image formats
SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif', '.webp'}


@dataclass
class ImageAnalysisResult:
    """Result of image analysis"""
    success: bool
    file_path: str
    file_name: str
    image_size: tuple[int, int]  # (width, height)
    format: str
    content_description: str
    experimental_context: str
    key_features: list[str]
    suggested_tags: list[str]
    error_message: Optional[str] = None


class ImageAnalyzer:
    """Analyzes images using vision LLM"""
    
    def __init__(self, vision_model_name: str = "doubao-seed-1-6-thinking"):
        """Initialize with vision model configuration"""
        self.model_name = vision_model_name
        self._init_vision_llm()
    
    def _init_vision_llm(self):
        """Initialize the vision LLM from config"""
        try:
            # Load config
            import json
            config_path = Path(__file__).parent.parent / "config" / "llm_config.json"
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            model_config = config["model_configs"].get(self.model_name)
            if not model_config:
                raise ValueError(f"Model {self.model_name} not found in config")
            
            # Get API key from environment
            import os
            api_key = os.environ.get(model_config["api_key_env"])
            if not api_key:
                raise ValueError(f"API key not found in environment: {model_config['api_key_env']}")
            
            # Create vision LLM instance with timeout
            self.vision_llm = ChatOpenAI(
                api_key=api_key,
                base_url=model_config["base_url"],
                model=model_config["model_name"],
                temperature=model_config.get("recommended_temperature", 0.4),
                max_tokens=2048,
                timeout=180,  # 3 minute timeout for API calls
                max_retries=1  # Only retry once on failure
            )
            
            logger.info(f"Initialized vision LLM: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize vision LLM: {e}")
            self.vision_llm = None
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            raise
    
    def get_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """Get basic image metadata"""
        try:
            with Image.open(image_path) as img:
                return {
                    "size": img.size,  # (width, height)
                    "format": img.format,
                    "mode": img.mode,
                    "info": img.info
                }
        except Exception as e:
            logger.error(f"Failed to get image metadata: {e}")
            return {}
    
    async def analyze_image(
        self, 
        image_path: str,
        context: Optional[str] = None,
        experiment_id: Optional[str] = None
    ) -> ImageAnalysisResult:
        """
        Analyze an image using vision LLM
        
        Args:
            image_path: Path to the image file
            context: Optional context about the experiment
            experiment_id: Optional experiment ID for context
            
        Returns:
            ImageAnalysisResult with analysis details
        """
        image_path = Path(image_path)
        
        # Check if file exists and is supported
        if not image_path.exists():
            return ImageAnalysisResult(
                success=False,
                file_path=str(image_path),
                file_name=image_path.name,
                image_size=(0, 0),
                format="unknown",
                content_description="",
                experimental_context="",
                key_features=[],
                suggested_tags=[],
                error_message=f"File not found: {image_path}"
            )
        
        if image_path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            return ImageAnalysisResult(
                success=False,
                file_path=str(image_path),
                file_name=image_path.name,
                image_size=(0, 0),
                format="unsupported",
                content_description="",
                experimental_context="",
                key_features=[],
                suggested_tags=[],
                error_message=f"Unsupported image format: {image_path.suffix}"
            )
        
        # Get metadata
        metadata = self.get_image_metadata(str(image_path))
        
        # Check if vision LLM is available
        if not self.vision_llm:
            # Fallback to basic metadata analysis
            return ImageAnalysisResult(
                success=True,
                file_path=str(image_path),
                file_name=image_path.name,
                image_size=metadata.get("size", (0, 0)),
                format=metadata.get("format", "unknown"),
                content_description="Image analysis unavailable (vision LLM not configured)",
                experimental_context="",
                key_features=[],
                suggested_tags=[],
                error_message="Vision LLM not available"
            )
        
        try:
            # Encode image
            base64_image = self.encode_image_to_base64(str(image_path))
            
            # Build prompt
            prompt = f"""Analyze this laboratory/experimental image and provide detailed insights.

Image: {image_path.name}
{f'Experiment Context: {context}' if context else ''}
{f'Experiment ID: {experiment_id}' if experiment_id else ''}

Please analyze the image and provide:

1. **Content Description**: What is shown in the image? Be specific about what you see.

2. **Experimental Context**: How does this relate to laboratory work or experiments? What type of data or results might this represent?

3. **Key Features**: List 3-5 important features or observations from the image:
   - Feature 1
   - Feature 2
   - etc.

4. **Suggested Tags**: Provide 3-5 relevant tags for categorizing this image:
   - Tag 1
   - Tag 2
   - etc.

Focus on scientific/experimental relevance. Be factual and specific."""
            
            # Get correct MIME type based on actual image format
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    actual_format = img.format.lower()
                
                # Map PIL formats to MIME types that Doubao supports
                format_mapping = {
                    'png': 'image/png',
                    'jpeg': 'image/jpeg', 
                    'jpg': 'image/jpeg',
                    'webp': 'image/webp',
                    'bmp': 'image/bmp',
                    'tiff': 'image/tiff',
                    'tif': 'image/tiff'
                }
                
                mime_type = format_mapping.get(actual_format, 'image/jpeg')
                logger.info(f"Using MIME type: {mime_type} for format: {actual_format}")
                
            except Exception as e:
                logger.warning(f"Could not detect image format, using jpeg: {e}")
                mime_type = 'image/jpeg'
            
            # Create message with image using correct MIME type
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            )
            
            # Get analysis from vision LLM with timeout handling
            import asyncio
            try:
                # Add an additional timeout wrapper
                response = await asyncio.wait_for(
                    self.vision_llm.ainvoke([message]), 
                    timeout=185  # Slightly longer than the client timeout (3 min)
                )
                analysis_text = response.content
            except asyncio.TimeoutError:
                logger.warning(f"Vision model timed out analyzing {image_path.name}")
                # Return basic info without AI analysis
                return ImageAnalysisResult(
                    success=True,
                    file_path=str(image_path),
                    file_name=image_path.name,
                    image_size=metadata.get("size", (0, 0)),
                    format=metadata.get("format", "unknown"),
                    content_description=f"Image analysis timed out. This is a {metadata.get('format', 'image')} file of size {metadata.get('size', 'unknown')}.",
                    experimental_context="Analysis unavailable due to timeout",
                    key_features=["Image metadata available", f"Format: {metadata.get('format', 'unknown')}"],
                    suggested_tags=["needs-manual-review"],
                    error_message="Vision model timeout - returning basic metadata only"
                )
            
            # Parse the response
            content_description = ""
            experimental_context = ""
            key_features = []
            suggested_tags = []
            
            # Simple parsing (could be improved with structured output)
            lines = analysis_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if "Content Description" in line:
                    current_section = "description"
                elif "Experimental Context" in line:
                    current_section = "context"
                elif "Key Features" in line:
                    current_section = "features"
                elif "Suggested Tags" in line:
                    current_section = "tags"
                elif current_section == "description" and not line.startswith("*"):
                    content_description += line + " "
                elif current_section == "context" and not line.startswith("*"):
                    experimental_context += line + " "
                elif current_section == "features" and line.startswith("-"):
                    key_features.append(line[1:].strip())
                elif current_section == "tags" and line.startswith("-"):
                    suggested_tags.append(line[1:].strip())
            
            # Clean up
            content_description = content_description.strip()
            experimental_context = experimental_context.strip()
            
            # Fallback if parsing didn't work well
            if not content_description:
                content_description = analysis_text[:500]
            
            return ImageAnalysisResult(
                success=True,
                file_path=str(image_path),
                file_name=image_path.name,
                image_size=metadata.get("size", (0, 0)),
                format=metadata.get("format", "unknown"),
                content_description=content_description,
                experimental_context=experimental_context,
                key_features=key_features[:5],  # Limit to 5
                suggested_tags=suggested_tags[:5]  # Limit to 5
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze image {image_path}: {e}")
            import traceback
            traceback.print_exc()
            
            return ImageAnalysisResult(
                success=False,
                file_path=str(image_path),
                file_name=image_path.name,
                image_size=metadata.get("size", (0, 0)),
                format=metadata.get("format", "unknown"),
                content_description="",
                experimental_context="",
                key_features=[],
                suggested_tags=[],
                error_message=str(e)
            )


# Convenience function for direct use
async def analyze_lab_image(
    image_path: str,
    context: Optional[str] = None,
    experiment_id: Optional[str] = None,
    vision_model: str = "doubao-seed-1-6-thinking"
) -> ImageAnalysisResult:
    """
    Convenience function to analyze a laboratory image
    
    Args:
        image_path: Path to the image
        context: Optional experimental context
        experiment_id: Optional experiment ID
        vision_model: Vision model to use (default: GLM-4.5V)
        
    Returns:
        ImageAnalysisResult with analysis
    """
    analyzer = ImageAnalyzer(vision_model_name=vision_model)
    return await analyzer.analyze_image(image_path, context, experiment_id)


# For synchronous use
def analyze_lab_image_sync(
    image_path: str,
    context: Optional[str] = None,
    experiment_id: Optional[str] = None,
    vision_model: str = "doubao-seed-1-6-thinking"
) -> ImageAnalysisResult:
    """
    Synchronous wrapper for image analysis
    """
    import asyncio
    return asyncio.run(analyze_lab_image(image_path, context, experiment_id, vision_model))