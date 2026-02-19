"""
Zia AI — Browser Executor
Selenium-based browser automation: open URLs, play YouTube.
"""

import time
from typing import Any, Dict, List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from app.executors.base import BaseExecutor


class BrowserExecutor(BaseExecutor):
    def get_supported_actions(self) -> List[str]:
        return ["browser.open_url", "browser.youtube_play"]

    async def execute(
        self, action_type: str, params: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        if action_type == "browser.open_url":
            self.validate_params(action_type, params, ["url"])
            return self._open_url(params["url"])
        elif action_type == "browser.youtube_play":
            self.validate_params(action_type, params, ["query"])
            return self._youtube_play(params["query"])
        raise ValueError(f"Unsupported: {action_type}")

    def _get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def _open_url(self, url: str) -> Dict:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        driver = self._get_driver()
        driver.get(url)
        return {"status": "url_opened", "url": url}

    def _youtube_play(self, query: str) -> Dict:
        driver = self._get_driver()
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(3)
        try:
            first_video = driver.find_element(By.ID, "video-title")
            first_video.click()
            return {"status": "youtube_playing", "query": query}
        except Exception as e:
            return {"status": "youtube_search_opened", "query": query, "note": str(e)}
