"""
Multi-provider LLM client for Hintly.

Supports both Anthropic (Claude) and OpenAI (GPT) models.
"""

from enum import Enum
from typing import Optional

from anthropic import Anthropic
from openai import OpenAI

from core.config import get_config


class LLMProvider(Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class LLMClient:
    """
    Unified interface for multiple LLM providers.
    
    Supports Anthropic (Claude) and OpenAI (GPT) models with
    automatic provider selection based on configuration.
    """
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: Optional provider override. If not provided,
                     uses LLM_PROVIDER from config.
        """
        self.config = get_config()
        
        if provider is None:
            provider_str = self.config.llm_provider.lower()
            self.provider = LLMProvider(provider_str)
        else:
            self.provider = provider
        
        # Initialize appropriate client
        if self.provider == LLMProvider.ANTHROPIC:
            if not self.config.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in .env")
            self.anthropic_client = Anthropic(api_key=self.config.anthropic_api_key)
        elif self.provider == LLMProvider.OPENAI:
            if not self.config.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in .env")
            self.openai_client = OpenAI(api_key=self.config.openai_api_key)
    
    def summarize(
        self,
        text: str,
        prompt: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a summary of text using the configured LLM.
        
        Args:
            text: Text to summarize
            prompt: Optional custom prompt
            context: Optional context (e.g., course name, topic)
            
        Returns:
            Summary text
        """
        if self.provider == LLMProvider.ANTHROPIC:
            return self._summarize_anthropic(text, prompt, context)
        elif self.provider == LLMProvider.OPENAI:
            return self._summarize_openai(text, prompt, context)
    
    def _summarize_anthropic(
        self,
        text: str,
        prompt: Optional[str],
        context: Optional[str]
    ) -> str:
        """Summarize using Claude."""
        system_prompt = "You are an expert educational assistant specializing in aerospace engineering and technical content. Generate clear, structured summaries in markdown format."
        
        if context:
            system_prompt += f"\n\nContext: {context}"
        
        user_prompt = prompt or (
            "Please provide a comprehensive summary of the following material. "
            "Include:\n"
            "1. Main topics covered\n"
            "2. Key concepts and equations\n"
            "3. Important points to remember\n"
            "4. Study notes\n\n"
            "Format your response in clean markdown."
        )
        
        full_prompt = f"{user_prompt}\n\n---\n\n{text}"
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        return message.content[0].text
    
    def _summarize_openai(
        self,
        text: str,
        prompt: Optional[str],
        context: Optional[str]
    ) -> str:
        """Summarize using GPT."""
        system_prompt = "You are an expert educational assistant specializing in aerospace engineering and technical content. Generate clear, structured summaries in markdown format."
        
        if context:
            system_prompt += f"\n\nContext: {context}"
        
        user_prompt = prompt or (
            "Please provide a comprehensive summary of the following material. "
            "Include:\n"
            "1. Main topics covered\n"
            "2. Key concepts and equations\n"
            "3. Important points to remember\n"
            "4. Study notes\n\n"
            "Format your response in clean markdown."
        )
        
        full_prompt = f"{user_prompt}\n\n---\n\n{text}"
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=4096,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def analyze_questions(
        self,
        questions: list[str],
        context: Optional[str] = None
    ) -> dict:
        """
        Analyze form questions using LLM.
        
        Args:
            questions: List of question texts
            context: Optional context (course info)
            
        Returns:
            Dict with analysis (topics, difficulty, suggestions)
        """
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        
        prompt = (
            "Analyze the following quiz/form questions:\n\n"
            f"{questions_text}\n\n"
            "Provide:\n"
            "1. Main topics covered\n"
            "2. Estimated difficulty level\n"
            "3. Study suggestions\n"
            "4. Key concepts to review"
        )
        
        if self.provider == LLMProvider.ANTHROPIC:
            return self._analyze_questions_anthropic(prompt, context)
        else:
            return self._analyze_questions_openai(prompt, context)
    
    def _analyze_questions_anthropic(self, prompt: str, context: Optional[str]) -> dict:
        """Analyze questions using Claude."""
        system = "You are analyzing educational quiz questions. Provide structured analysis."
        if context:
            system += f" Context: {context}"
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {"analysis": message.content[0].text, "provider": "anthropic"}
    
    def _analyze_questions_openai(self, prompt: str, context: Optional[str]) -> dict:
        """Analyze questions using GPT."""
        system = "You are analyzing educational quiz questions. Provide structured analysis."
        if context:
            system += f" Context: {context}"
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Use mini for simpler analysis task
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.3
        )
        
        return {"analysis": response.choices[0].message.content, "provider": "openai"}
