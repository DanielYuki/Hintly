"""
Browser-based Google Forms scraper using Playwright.

Replaces forms_api.py to work with ANY form (teacher-assigned, public, shared).
"""

from dataclasses import dataclass, field
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


@dataclass
class FormQuestion:
    """Represents a question in a Google Form."""
    
    title: str
    type: str
    required: bool
    options: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class GoogleForm:
    """Represents a Google Form."""
    
    title: str
    description: str
    questions: list[FormQuestion]
    form_url: str = ""


class BrowserFormsClient:
    """
    Extract form data via browser automation.
    
    Works with ANY Google Form:
    - Teacher-assigned forms
    - Public forms
    - Shared forms
    
    Unlike the Forms API, this doesn't require form ownership.
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize browser forms client.
        
        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.headless = headless
    
    def _get_authenticated_context(self, playwright):
        """
        Create a persistent browser context that maintains Google login.
        
        Uses saved browser session from setup_browser_login.py script.
        If not logged in, user needs to run setup first.
        """
        from pathlib import Path
        
        # Use persistent context to maintain login
        user_data_dir = Path.home() / ".hintly" / "browser_data"
        
        if not user_data_dir.exists():
            raise Exception(
                "Browser session not found. Please run setup first:\n"
                "PYTHONPATH=. uv run python skills/classroom-forms-helper/scripts/setup_browser_login.py"
            )
        
        # Launch with persistent context (reuses saved session)
        browser = playwright.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        return browser, browser
    
    def get_form(self, form_url: str, timeout: int = 20000) -> GoogleForm:
        """
        Scrape form structure from any Google Form.
        
        Args:
            form_url: Google Form URL
            timeout: Page load timeout in milliseconds
            
        Returns:
            GoogleForm object with questions
            
        Raises:
            PlaywrightTimeout: If form doesn't load in time
            Exception: For other browser errors
        """
        with sync_playwright() as p:
            browser, context = self._get_authenticated_context(p)
            page = context.new_page()
            
            try:
                # Navigate to form
                page.goto(form_url, wait_until="networkidle", timeout=timeout)
                
                # Try multiple selectors for form items
                selectors = [
                    '[role="listitem"]',  # Modern Google Forms (works!)
                    '.freebirdFormviewerViewItemsItemItem',  # Legacy selector
                    '[data-item-id]',  # Alternative
                ]
                
                form_items_selector = None
                for selector in selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        form_items_selector = selector
                        break
                    except PlaywrightTimeout:
                        continue
                
                if not form_items_selector:
                    # Form might require authentication or have different structure
                    # Try to get page title at least
                    title_elem = page.query_selector('title')
                    page_title = title_elem.inner_text() if title_elem else "Unknown"
                    
                    raise Exception(
                        f"Could not find form questions on page. "
                        f"Page title: '{page_title}'. "
                        f"This form may require Google authentication or have restricted access."
                    )
                
                # Extract title
                title_elem = page.query_selector('.freebirdFormviewerViewHeaderTitle')
                title = title_elem.inner_text() if title_elem else "Untitled Form"
                
                # Extract description
                desc_elem = page.query_selector('.freebirdFormviewerViewHeaderDescription')
                description = desc_elem.inner_text() if desc_elem else ""
                
                # Extract questions using the selector that worked
                questions = self._extract_questions(page, form_items_selector)
                
                return GoogleForm(
                    title=title,
                    description=description,
                    questions=questions,
                    form_url=form_url
                )
                
            finally:
                browser.close()
    
    def _extract_questions(self, page, items_selector: str = '[role="listitem"]') -> list[FormQuestion]:
        """Extract all questions from the page."""
        questions = []
        items = page.query_selector_all(items_selector)
        
        for item in items:
            # Modern Google Forms use different structure
            # Try to find question title with multiple possible selectors
            title_selectors = [
                '.freebirdFormviewerComponentsQuestionBaseTitle',
                '[role="heading"]',
                'div[jsname] span',  # Generic title span
            ]
            
            title_elem = None
            for selector in title_selectors:
                title_elem = item.query_selector(selector)
                if title_elem:
                    break
            
            if not title_elem:
                continue
            
            q_title = title_elem.inner_text().strip()
            if not q_title or len(q_title) < 2:  # Skip empty or very short titles
                continue
            
            # Question description
            desc_elem = item.query_selector('.freebirdFormviewerComponentsQuestionBaseDescription')
            q_description = desc_elem.inner_text().strip() if desc_elem else ""
            
            # Check if required - look for asterisk or required indicator
            required_indicators = [
                '.freebirdFormviewerComponentsQuestionBaseRequiredAsterisk',
                '[aria-required="true"]',
                'span:has-text("*")'
            ]
            required = False
            for indicator in required_indicators:
                if item.query_selector(indicator):
                    required = True
                    break
            
            # Detect question type and extract options
            q_type, options = self._detect_question_type(item)
            
            questions.append(FormQuestion(
                title=q_title,
                type=q_type,
                required=required,
                options=options,
                description=q_description
            ))
        
        return questions
    
    def _detect_question_type(self, item) -> tuple[str, list[str]]:
        """
        Detect question type and extract options if applicable.
        
        Returns:
            Tuple of (question_type, options_list)
        """
        options = []
        
        # Multiple choice (radio buttons)
        if item.query_selector('.freebirdFormviewerComponentsQuestionRadioRoot'):
            q_type = "MULTIPLE_CHOICE"
            option_elems = item.query_selector_all(
                '.freebirdFormviewerComponentsQuestionRadioLabel'
            )
            options = [opt.inner_text().strip() for opt in option_elems if opt.inner_text().strip()]
        
        # Checkboxes
        elif item.query_selector('.freebirdFormviewerComponentsQuestionCheckboxRoot'):
            q_type = "CHECKBOXES"
            option_elems = item.query_selector_all(
                '.freebirdFormviewerComponentsQuestionCheckboxLabel'
            )
            options = [opt.inner_text().strip() for opt in option_elems if opt.inner_text().strip()]
        
        # Dropdown
        elif item.query_selector('.freebirdFormviewerComponentsQuestionSelectRoot'):
            q_type = "DROPDOWN"
            option_elems = item.query_selector_all(
                '.freebirdFormviewerComponentsQuestionSelectOption'
            )
            options = [opt.inner_text().strip() for opt in option_elems if opt.inner_text().strip()]
        
        # Short answer
        elif item.query_selector('.freebirdFormviewerComponentsQuestionTextShortText'):
            q_type = "SHORT_ANSWER"
        
        # Paragraph
        elif item.query_selector('.freebirdFormviewerComponentsQuestionTextParagraph'):
            q_type = "PARAGRAPH"
        
        # Linear scale
        elif item.query_selector('.freebirdFormviewerComponentsQuestionScaleRoot'):
            q_type = "SCALE"
            # Could extract scale range here if needed
        
        # Date
        elif item.query_selector('.freebirdFormviewerComponentsQuestionDateDateInput'):
            q_type = "DATE"
        
        # Time
        elif item.query_selector('.freebirdFormviewerComponentsQuestionTimeTimeInput'):
            q_type = "TIME"
        
        # File upload
        elif item.query_selector('.freebirdFormviewerComponentsQuestionFileUploadRoot'):
            q_type = "FILE_UPLOAD"
        
        else:
            q_type = "UNKNOWN"
        
        return q_type, options
