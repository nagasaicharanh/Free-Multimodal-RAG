"""
Google Gemini API client for multimodal vision understanding.
Uses Google Gemini 1.5 Flash with free tier (1500 req/day).
"""
import base64
from typing import Optional
import google.generativeai as genai
from src.config import GOOGLE_API_KEY, GOOGLE_MODEL_NAME, MAX_IMAGE_DESCRIPTION_LENGTH


class GeminiClient:
    """Interface to Google Gemini API for vision understanding."""

    def __init__(self, api_key: str = GOOGLE_API_KEY, model: str = GOOGLE_MODEL_NAME):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key
            model: Model name (default: gemini-1.5-flash)
        """
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        # Use gemini-2.0-flash or gemini-pro depending on availability
        try:
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            self.model_name = "gemini-2.0-flash"
        except:
            try:
                self.model = genai.GenerativeModel("gemini-1.5-pro")
                self.model_name = "gemini-1.5-pro"
            except:
                self.model = genai.GenerativeModel("gemini-pro")
                self.model_name = "gemini-pro"

    def describe_image(self, image_base64: str, image_format: str = "png") -> str:
        """
        Generate a detailed description of an image.
        
        Args:
            image_base64: Base64-encoded image
            image_format: Image format (png, jpeg, etc.)
            
        Returns:
            Natural language description of the image
        """
        prompt = """
Analyze this image/chart and provide a detailed description. Focus on:
1. What is shown in the image?
2. Key data, trends, or insights if it's a chart
3. Important details for a Q&A system

Keep the description clear and concise.
"""
        
        return self._call_api_with_image(
            prompt=prompt,
            image_base64=image_base64,
            image_format=image_format,
            max_output_tokens=MAX_IMAGE_DESCRIPTION_LENGTH
        )

    def analyze_chart(self, image_base64: str, image_format: str = "png") -> str:
        """
        Analyze a chart and extract key insights.
        
        Args:
            image_base64: Base64-encoded chart image
            image_format: Image format
            
        Returns:
            Analysis of the chart
        """
        prompt = """
This is a chart or data visualization. Please:
1. Identify the type of chart
2. Extract the main message or trend
3. List key data points or statistics shown
4. Explain what insights this chart conveys

Be precise and factual.
"""
        
        return self._call_api_with_image(
            prompt=prompt,
            image_base64=image_base64,
            image_format=image_format,
            max_output_tokens=MAX_IMAGE_DESCRIPTION_LENGTH
        )

    def _call_api_with_image(
        self,
        prompt: str,
        image_base64: str,
        image_format: str = "png",
        max_output_tokens: int = 1000
    ) -> str:
        """
        Make a multimodal API call to Gemini with image.
        
        Args:
            prompt: Text prompt
            image_base64: Base64-encoded image
            image_format: Image format
            max_output_tokens: Max tokens in response
            
        Returns:
            Generated text
        """
        try:
            # Prepare image data
            image_data = {
                "mime_type": f"image/{image_format}",
                "data": image_base64,
            }
            
            # Make API call
            response = self.model.generate_content(
                [prompt, {"inline_data": image_data}],
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_output_tokens,
                )
            )
            
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return f"Error: {str(e)}"


if __name__ == "__main__":
    # Example usage (requires GOOGLE_API_KEY)
    try:
        # Create a simple test image
        from PIL import Image
        import io
        
        img = Image.new('RGB', (200, 200), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        b64_str = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        client = GeminiClient()
        description = client.describe_image(b64_str)
        print(f"Image Description: {description}")
    except ValueError as e:
        print(f"Setup error: {e}")
    except Exception as e:
        print(f"Error: {e}")
