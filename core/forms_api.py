"""
Google Forms API wrapper for Hintly.

Reads form structure and questions from Google Forms.
"""

import re
from dataclasses import dataclass
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from core.auth import OAuth2Flow


@dataclass
class FormQuestion:
    """Represents a question in a Google Form."""
    
    id: str
    title: str
    type: str  # MULTIPLE_CHOICE, SHORT_ANSWER, PARAGRAPH, etc.
    required: bool
    options: list[str] = None  # For multiple choice questions
    description: str = ""
    
    def __post_init__(self):
        if self.options is None:
            self.options = []


@dataclass
class GoogleForm:
    """Represents a Google Form."""
    
    id: str
    title: str
    description: str
    questions: list[FormQuestion]
    respondent_uri: str = ""
    
    def __post_init__(self):
        if self.questions is None:
            self.questions = []


class FormsClient:
    """
    Google Forms API client for reading form structure.
    
    Can read form questions and structure, but cannot submit responses
    (Forms API restriction).
    """
    
    def __init__(self, credentials: Optional[Credentials] = None):
        """
        Initialize Forms client.
        
        Args:
            credentials: Optional Google credentials. If not provided,
                        will use stored token.
        """
        if credentials is None:
            flow = OAuth2Flow()
            credentials = flow.get_credentials()
            if not credentials:
                raise ValueError("Not authenticated. Run auth.py --setup first.")
        
        self.service = build("forms", "v1", credentials=credentials)
    
    @staticmethod
    def extract_form_id_from_url(url: str) -> str:
        """
        Extract Google Form ID from URL.
        
        Args:
            url: Google Form URL
            
        Returns:
            Form ID
            
        Examples:
            >>> FormsClient.extract_form_id_from_url(
            ...     "https://docs.google.com/forms/d/1ABC123/edit"
            ... )
            '1ABC123'
        """
        # Pattern: /forms/d/e/{FORM_ID} (public viewform links)
        pattern = r"/forms/d/e/([a-zA-Z0-9_-]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        # Pattern: /forms/d/{FORM_ID} (edit links)
        pattern = r"/forms/d/([a-zA-Z0-9_-]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        # Pattern: formId= parameter
        pattern = r"formId=([a-zA-Z0-9_-]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        raise ValueError(f"Could not extract form ID from URL: {url}")
    
    def get_form(self, form_id: str) -> GoogleForm:
        """
        Get form structure including all questions.
        
        Args:
            form_id: Google Form ID
            
        Returns:
            GoogleForm object with questions
        """
        # Get form metadata and questions
        form = self.service.forms().get(formId=form_id).execute()
        
        # Parse questions
        questions = []
        for item in form.get("items", []):
            question_item = item.get("questionItem")
            if not question_item:
                continue
            
            question_data = question_item.get("question", {})
            
            # Get question type and options
            question_type = "UNKNOWN"
            options = []
            
            if "choiceQuestion" in question_data:
                question_type = "MULTIPLE_CHOICE"
                choice_options = question_data["choiceQuestion"].get("options", [])
                options = [opt.get("value", "") for opt in choice_options]
            elif "textQuestion" in question_data:
                text_type = question_data["textQuestion"].get("paragraph", False)
                question_type = "PARAGRAPH" if text_type else "SHORT_ANSWER"
            elif "scaleQuestion" in question_data:
                question_type = "SCALE"
            elif "dateQuestion" in question_data:
                question_type = "DATE"
            elif "timeQuestion" in question_data:
                question_type = "TIME"
            
            question = FormQuestion(
                id=question_data.get("questionId", ""),
                title=item.get("title", ""),
                type=question_type,
                required=question_data.get("required", False),
                options=options,
                description=item.get("description", "")
            )
            questions.append(question)
        
        return GoogleForm(
            id=form["formId"],
            title=form.get("info", {}).get("title", ""),
            description=form.get("info", {}).get("description", ""),
            questions=questions,
            respondent_uri=form.get("responderUri", "")
        )
    
    def get_form_from_url(self, url: str) -> GoogleForm:
        """
        Get form structure from Google Form URL.
        
        Args:
            url: Google Form URL
            
        Returns:
            GoogleForm object
        """
        form_id = self.extract_form_id_from_url(url)
        return self.get_form(form_id)
    
    def get_form_structure(self, form_id: str) -> dict:
        """
        Get raw form structure as dictionary.
        
        Args:
            form_id: Google Form ID
            
        Returns:
            Raw form data as dict
        """
        return self.service.forms().get(formId=form_id).execute()
