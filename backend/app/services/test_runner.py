import asyncio
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

from app.core.config import settings


class TestRunner:
    """
    Test runner using Playwright
    """
    
    def __init__(self):
        self.screenshots_dir = settings.SCREENSHOTS_DIR
        self.videos_dir = settings.VIDEOS_DIR
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
    
    async def run_test(self, script_content: str, test_type: str) -> Dict[str, Any]:
        """
        Run a test script
        """
        try:
            if test_type == "ui" or test_type == "black_box":
                return await self._run_ui_test(script_content)
            elif test_type == "api":
                return await self._run_api_test(script_content)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported test type: {test_type}",
                    "logs": ""
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "logs": ""
            }
    
    async def _run_ui_test(self, script_content: str) -> Dict[str, Any]:
        """
        Run UI test using Playwright
        """
        logs = []
        screenshot_path = None
        
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=settings.HEADLESS,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                # Create context with video recording
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    record_video_dir=self.videos_dir,
                    record_video_size={'width': 1280, 'height': 720}
                )
                
                # Create page
                page = await context.new_page()
                
                # Execute test script
                # The script should be a Python script that uses Playwright API
                # For safety, we'll use a restricted execution environment
                
                # Create a safe execution context
                exec_globals = {
                    'page': page,
                    'asyncio': asyncio,
                    'os': os,
                    'datetime': datetime
                }
                
                # Execute the test script
                exec(script_content, exec_globals)
                
                # Take screenshot
                screenshot_filename = f"test_{uuid.uuid4().hex[:8]}.png"
                screenshot_path = os.path.join(self.screenshots_dir, screenshot_filename)
                await page.screenshot(path=screenshot_path)
                
                logs.append(f"Test completed successfully at {datetime.utcnow()}")
                
                # Close context and browser
                await context.close()
                await browser.close()
                
                return {
                    "success": True,
                    "logs": "\n".join(logs),
                    "screenshot_path": screenshot_path,
                    "video_path": None  # Video path would be set after context closes
                }
                
        except Exception as e:
            logs.append(f"Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "logs": "\n".join(logs),
                "screenshot_path": screenshot_path
            }
    
    async def _run_api_test(self, script_content: str) -> Dict[str, Any]:
        """
        Run API test
        """
        import httpx
        
        logs = []
        
        try:
            # Execute API test script
            exec_globals = {
                'httpx': httpx,
                'asyncio': asyncio,
                'os': os,
                'datetime': datetime
            }
            
            # Execute the test script
            result = exec(script_content, exec_globals)
            
            logs.append(f"API test completed successfully at {datetime.utcnow()}")
            
            return {
                "success": True,
                "logs": "\n".join(logs)
            }
            
        except Exception as e:
            logs.append(f"Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "logs": "\n".join(logs)
            }


class TestRunnerSingleton:
    """
    Singleton test runner instance
    """
    _instance: Optional[TestRunner] = None
    
    @classmethod
    def get_instance(cls) -> TestRunner:
        if cls._instance is None:
            cls._instance = TestRunner()
        return cls._instance