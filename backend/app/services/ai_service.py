import os
from typing import Optional, Dict, Any
from openai import AsyncOpenAI

from app.core.config import settings


class AIService:
    """
    AI service for test script generation
    """
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_test_script(
        self,
        description: str,
        test_type: str = "black_box",
        target_url: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate test script using AI
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "script": None
            }
        
        try:
            # Build prompt based on test type
            prompt = self._build_prompt(description, test_type, target_url, additional_context)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(test_type)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract script from response
            script = response.choices[0].message.content
            
            # Clean up script
            script = self._clean_script(script)
            
            return {
                "success": True,
                "script": script,
                "model": "gpt-4",
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "script": None
            }
    
    def _get_system_prompt(self, test_type: str) -> str:
        """
        Get system prompt based on test type
        """
        base_prompt = """You are an expert test automation engineer. 
Your task is to generate Python test scripts using Playwright for browser automation.
The scripts should be:
1. Well-structured and readable
2. Include proper error handling
3. Use appropriate waits and assertions
4. Follow best practices for test automation

Output ONLY the Python code, no explanations or markdown formatting."""
        
        if test_type == "black_box" or test_type == "ui":
            return base_prompt + """
Focus on UI testing:
- Navigate to URLs
- Interact with elements (click, fill, select)
- Assert element states and content
- Take screenshots for verification
- Handle different browsers and viewports"""
        
        elif test_type == "api":
            return base_prompt + """
Focus on API testing:
- Use httpx for HTTP requests
- Test different HTTP methods
- Validate response status codes and body
- Handle authentication
- Test error scenarios"""
        
        else:
            return base_prompt
    
    def _build_prompt(
        self,
        description: str,
        test_type: str,
        target_url: Optional[str],
        additional_context: Optional[str]
    ) -> str:
        """
        Build prompt for AI
        """
        prompt = f"Generate a {test_type} test script for the following scenario:\n\n"
        prompt += f"Description: {description}\n\n"
        
        if target_url:
            prompt += f"Target URL: {target_url}\n\n"
        
        if additional_context:
            prompt += f"Additional Context:\n{additional_context}\n\n"
        
        prompt += """Requirements:
1. Use Playwright for browser automation (for UI tests)
2. Include proper imports
3. Add comments explaining each step
4. Handle potential errors gracefully
5. Take screenshots at key points
6. Use async/await syntax

Generate the complete Python test script:"""
        
        return prompt
    
    def _clean_script(self, script: str) -> str:
        """
        Clean up generated script
        """
        # Remove markdown code blocks if present
        if script.startswith("```python"):
            script = script[9:]
        if script.startswith("```"):
            script = script[3:]
        if script.endswith("```"):
            script = script[:-3]
        
        # Remove leading/trailing whitespace
        script = script.strip()
        
        return script
    
    async def analyze_page_elements(self, url: str) -> Dict[str, Any]:
        """
        Analyze page elements using AI (for generating better test scripts)
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "elements": None
            }
        
        try:
            prompt = f"""Analyze the following URL and suggest key elements to test:
URL: {url}

Please provide:
1. Main interactive elements (buttons, inputs, links)
2. Key content areas to verify
3. Navigation elements
4. Form elements if any
5. Recommended test scenarios

Format as a structured analysis:"""
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a QA expert analyzing web pages for test automation."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis,
                "url": url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "elements": None
            }
    
    async def suggest_test_improvements(
        self,
        script: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest improvements for a test script
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "suggestions": None
            }
        
        try:
            prompt = f"""Review and suggest improvements for this test script:

```python
{script}
```"""
            
            if error_message:
                prompt += f"""

The script failed with this error:
{error_message}

Please suggest fixes:"""
            else:
                prompt += "\n\nPlease suggest improvements for reliability, readability, and coverage."
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a test automation expert reviewing test scripts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            suggestions = response.choices[0].message.content
            
            return {
                "success": True,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "suggestions": None
            }


# Singleton instance
ai_service = AIService()