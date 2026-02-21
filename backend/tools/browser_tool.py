"""
Browser tool — YouTube search, playback, and media control via Selenium.

Uses a singleton YouTubeSession so the browser stays alive across tool calls.
"""

import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from tools.base_tool import BaseTool

logger = logging.getLogger("zia.tools.browser")


class YouTubeSession:
    """
    Singleton browser session for YouTube.
    One driver instance shared across all tool calls.
    """

    _instance: "YouTubeSession | None" = None
    _driver: webdriver.Chrome | None = None

    @classmethod
    def get(cls) -> "YouTubeSession":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def driver(self) -> webdriver.Chrome:
        """Return a healthy driver, creating one if needed."""
        if not self._is_alive():
            logger.info("Creating new Chrome session for YouTube.")
            self._create_driver()
        return self._driver

    def _is_alive(self) -> bool:
        """Check if the current driver session is still usable."""
        if self._driver is None:
            return False
        try:
            _ = self._driver.title
            return True
        except WebDriverException:
            logger.warning("Chrome session died. Will recreate.")
            self._driver = None
            return False

    def _create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )


# ── Tools ──────────────────────────────────────────────


class YouTubeTool(BaseTool):
    name = "play_youtube"
    description = (
        "Search and play a video on YouTube. "
        "Use this when the user asks to play music, a video, or search YouTube."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for YouTube (e.g. 'lofi hip hop radio').",
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    }

    def execute(self, *, query: str) -> dict:
        session = YouTubeSession.get()
        driver = session.driver

        try:
            search_url = (
                f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            )
            driver.get(search_url)
            time.sleep(3)
            first_video = driver.find_element(By.ID, "video-title")
            first_video.click()
            return {"status": "playing", "query": query}
        except Exception as e:
            logger.error("play_youtube failed: %s", e)
            return {"error": str(e)}


class YouTubeControlTool(BaseTool):
    name = "youtube_control"
    description = (
        "Control YouTube playback in the current browser session. "
        "Use this when the user says 'next song', 'skip', 'pause', 'resume', "
        "'previous', 'next track', or similar media control commands."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["next", "pause", "resume", "previous"],
                "description": "The playback action: next, pause, resume, or previous.",
            },
        },
        "required": ["action"],
        "additionalProperties": False,
    }

    def execute(self, *, action: str) -> dict:
        action = action.lower().strip()

        if action not in ("next", "previous", "pause", "resume"):
            return {"error": f"Unknown action: {action}. Use: next, pause, resume, previous."}

        session = YouTubeSession.get()
        driver = session.driver

        try:
            if "youtube.com" not in driver.current_url:
                return {"error": "No YouTube session active. Use play_youtube first."}

            if action in ("next", "previous"):
                return self._send_nav_key(driver, action)
            else:
                return self._handle_play_pause(driver, action)

        except Exception as e:
            logger.error("youtube_control(%s) failed: %s", action, e)
            return {"error": str(e)}

    @staticmethod
    def _send_nav_key(driver, action: str) -> dict:
        """Next / Previous via keyboard shortcuts."""
        key = Keys.SHIFT + "n" if action == "next" else Keys.SHIFT + "p"
        label = "Skipped to next video" if action == "next" else "Went to previous video"

        try:
            player = driver.find_element(By.ID, "movie_player")
            player.click()
            time.sleep(0.3)
        except Exception:
            pass

        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(key)
        return {"status": label}

    @staticmethod
    def _handle_play_pause(driver, action: str) -> dict:
        """Pause / Resume using explicit state detection — never toggles."""
        is_paused = driver.execute_script(
            "return document.querySelector('video')?.paused"
        )

        if is_paused is None:
            return {"error": "No video element found on page."}

        if action == "pause" and is_paused:
            return {"status": "Already paused"}

        if action == "resume" and not is_paused:
            return {"status": "Already playing"}

        # Click the play/pause button to change state
        play_btn = driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button")
        play_btn.click()

        if action == "pause":
            return {"status": "Paused playback"}
        else:
            return {"status": "Resumed playback"}
