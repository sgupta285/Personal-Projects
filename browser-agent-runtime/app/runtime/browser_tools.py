from __future__ import annotations

from pathlib import Path
from typing import Any

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from app.config import get_settings

settings = get_settings()


class BrowserToolkit:
    def __init__(self, *, headless: bool = True) -> None:
        self.headless = headless
        self._playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def __aenter__(self) -> "BrowserToolkit":
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def navigate(self, url: str) -> dict[str, Any]:
        assert self.page is not None
        response = await self.page.goto(url, wait_until="domcontentloaded")
        return {"url": self.page.url, "status": getattr(response, "status", None)}

    async def click(self, selector: str) -> dict[str, Any]:
        assert self.page is not None
        await self.page.click(selector)
        return {"clicked": selector, "url": self.page.url}

    async def type(self, selector: str, text: str) -> dict[str, Any]:
        assert self.page is not None
        await self.page.fill(selector, text)
        return {"filled": selector}

    async def fill_form(self, fields: dict[str, str]) -> dict[str, Any]:
        assert self.page is not None
        for selector, text in fields.items():
            await self.page.fill(selector, text)
        return {"filled_fields": list(fields.keys())}

    async def extract_text(self, selector: str) -> dict[str, Any]:
        assert self.page is not None
        text = await self.page.locator(selector).inner_text()
        return {"selector": selector, "text": text[:5000]}

    async def wait_for(self, selector: str, timeout_ms: int = 5000) -> dict[str, Any]:
        assert self.page is not None
        await self.page.wait_for_selector(selector, timeout=timeout_ms)
        return {"selector": selector, "ready": True}

    async def screenshot(self, name: str) -> dict[str, Any]:
        assert self.page is not None
        safe_name = f"{name}.png"
        path = settings.artifact_dir / safe_name
        await self.page.screenshot(path=str(path), full_page=True)
        return {"path": str(path)}

    async def submit(self, selector: str) -> dict[str, Any]:
        return await self.click(selector)

    async def dom_summary(self) -> dict[str, Any]:
        assert self.page is not None
        title = await self.page.title()
        body_preview = await self.page.locator("body").inner_text()
        return {"title": title, "body_preview": body_preview[:1000]}


class DryRunBrowserToolkit:
    '''
    Lightweight stand-in used when the operator wants to validate plans without touching a real browser.
    '''

    def __init__(self, *, headless: bool = True) -> None:
        self.headless = headless
        self.current_url = "about:blank"

    async def __aenter__(self) -> "DryRunBrowserToolkit":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def navigate(self, url: str) -> dict[str, Any]:
        self.current_url = url
        return {"url": url, "status": 200, "dry_run": True}

    async def click(self, selector: str) -> dict[str, Any]:
        return {"clicked": selector, "url": self.current_url, "dry_run": True}

    async def type(self, selector: str, text: str) -> dict[str, Any]:
        return {"filled": selector, "text_length": len(text), "dry_run": True}

    async def fill_form(self, fields: dict[str, str]) -> dict[str, Any]:
        return {"filled_fields": list(fields.keys()), "dry_run": True}

    async def extract_text(self, selector: str) -> dict[str, Any]:
        return {"selector": selector, "text": "Dry-run content preview.", "dry_run": True}

    async def wait_for(self, selector: str, timeout_ms: int = 5000) -> dict[str, Any]:
        return {"selector": selector, "ready": True, "timeout_ms": timeout_ms, "dry_run": True}

    async def screenshot(self, name: str) -> dict[str, Any]:
        path = Path(settings.artifact_dir) / f"{name}.txt"
        path.write_text(f"dry-run screenshot placeholder for {name}\\n", encoding="utf-8")
        return {"path": str(path), "dry_run": True}

    async def submit(self, selector: str) -> dict[str, Any]:
        return {"clicked": selector, "submitted": False, "dry_run": True}

    async def dom_summary(self) -> dict[str, Any]:
        return {"title": "Dry Run", "body_preview": "No browser page was opened."}
