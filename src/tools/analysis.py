"""
Analysis Utilities for the Multi-Agent Virtual Company.

This module provides text processing and analysis utilities
used by the Analyst and other agents for data processing.
"""

import re
from collections import Counter
from typing import Optional
from datetime import datetime
from loguru import logger

from src.schemas.models import (
    ResearchData,
    SearchResult,
    AnalysisSummary,
    KeyInsight,
)


class TextAnalyzer:
    """
    Text analysis utilities for processing research data.
    
    Provides methods for text cleaning, keyword extraction,
    sentiment indicators, and data quality assessment.
    """
    
    # Common stop words to filter out
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "it", "its", "this", "that", "these", "those", "i", "you", "he",
        "she", "we", "they", "what", "which", "who", "when", "where", "why",
        "how", "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "just", "also", "now", "here", "there",
    }
    
    # Sentiment indicator words
    POSITIVE_WORDS = {
        "growth", "increase", "profit", "gain", "positive", "strong", "bullish",
        "surge", "rise", "up", "boom", "success", "successful", "opportunity",
        "opportunities", "improve", "improved", "improving", "beat", "exceed",
        "exceeded", "outperform", "rally", "breakthrough", "innovation", "leading",
        "best", "record", "high", "higher", "optimistic", "confident", "promising",
    }
    
    NEGATIVE_WORDS = {
        "decline", "decrease", "loss", "drop", "negative", "weak", "bearish",
        "fall", "down", "crash", "failure", "failed", "risk", "risks", "concern",
        "concerns", "worried", "worry", "miss", "missed", "underperform", "sell",
        "selloff", "worst", "low", "lower", "pessimistic", "uncertain", "warning",
        "layoff", "layoffs", "cut", "cuts", "lawsuit", "investigation", "debt",
    }
    
    def __init__(self):
        """Initialize the text analyzer."""
        logger.debug("TextAnalyzer initialized")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces and basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords(
        self,
        text: str,
        top_n: int = 10,
        min_word_length: int = 3,
    ) -> list[tuple[str, int]]:
        """
        Extract top keywords from text.
        
        Args:
            text: Text to analyze
            top_n: Number of top keywords to return
            min_word_length: Minimum word length to consider
            
        Returns:
            List of (keyword, count) tuples
        """
        cleaned = self.clean_text(text)
        words = cleaned.split()
        
        # Filter words
        filtered_words = [
            word for word in words
            if len(word) >= min_word_length
            and word not in self.STOP_WORDS
            and word.isalpha()
        ]
        
        # Count frequencies
        word_counts = Counter(filtered_words)
        
        return word_counts.most_common(top_n)
    
    def calculate_sentiment_score(self, text: str) -> tuple[float, str]:
        """
        Calculate a simple sentiment score from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (score from -1 to 1, sentiment label)
        """
        cleaned = self.clean_text(text)
        words = set(cleaned.split())
        
        positive_count = len(words & self.POSITIVE_WORDS)
        negative_count = len(words & self.NEGATIVE_WORDS)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0, "neutral"
        
        score = (positive_count - negative_count) / total
        
        if score > 0.3:
            sentiment = "bullish"
        elif score > 0.1:
            sentiment = "neutral"  # slightly positive but still neutral
        elif score < -0.3:
            sentiment = "bearish"
        elif score < -0.1:
            sentiment = "neutral"  # slightly negative but still neutral
        else:
            sentiment = "neutral"
        
        # Check for mixed signals
        if positive_count > 2 and negative_count > 2:
            sentiment = "mixed"
        
        return round(score, 3), sentiment
    
    def assess_data_quality(self, research_data: ResearchData) -> float:
        """
        Assess the quality of research data on a scale of 0-1.
        
        Factors considered:
        - Number of sources
        - Diversity of sources
        - Recency of data
        - Content length
        
        Args:
            research_data: ResearchData to assess
            
        Returns:
            Quality score from 0 to 1
        """
        score = 0.0
        
        # Factor 1: Number of sources (0-0.3)
        source_count = research_data.sources_count
        if source_count >= 5:
            score += 0.3
        elif source_count >= 3:
            score += 0.2
        elif source_count >= 1:
            score += 0.1
        
        # Factor 2: Content length (0-0.3)
        content_length = len(research_data.raw_content)
        if content_length >= 5000:
            score += 0.3
        elif content_length >= 2000:
            score += 0.2
        elif content_length >= 500:
            score += 0.1
        
        # Factor 3: Source diversity (0-0.2)
        if research_data.search_results:
            domains = set()
            for result in research_data.search_results:
                # Extract domain from URL
                match = re.search(r'https?://([^/]+)', result.url)
                if match:
                    domains.add(match.group(1))
            
            domain_count = len(domains)
            if domain_count >= 4:
                score += 0.2
            elif domain_count >= 2:
                score += 0.1
        
        # Factor 4: Presence of researcher notes (0-0.1)
        if research_data.researcher_notes:
            score += 0.1
        
        # Factor 5: Recent data (0-0.1)
        if research_data.search_results:
            has_recent = any(
                result.published_date is not None
                for result in research_data.search_results
            )
            if has_recent:
                score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def extract_numbers(self, text: str) -> list[dict]:
        """
        Extract numbers and their context from text.
        
        Useful for finding statistics, prices, percentages, etc.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of dicts with number and context
        """
        numbers = []
        
        # Pattern for percentages
        pct_pattern = r'(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(pct_pattern, text):
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            numbers.append({
                "value": float(match.group(1)),
                "type": "percentage",
                "context": context,
            })
        
        # Pattern for currency
        currency_pattern = r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(billion|million|thousand|B|M|K)?'
        for match in re.finditer(currency_pattern, text, re.IGNORECASE):
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            
            value = float(match.group(1).replace(",", ""))
            multiplier = match.group(2)
            if multiplier:
                multiplier = multiplier.lower()
                if multiplier in ["billion", "b"]:
                    value *= 1_000_000_000
                elif multiplier in ["million", "m"]:
                    value *= 1_000_000
                elif multiplier in ["thousand", "k"]:
                    value *= 1_000
            
            numbers.append({
                "value": value,
                "type": "currency",
                "context": context,
            })
        
        return numbers
    
    def summarize_sources(self, search_results: list[SearchResult]) -> str:
        """
        Create a summary of sources used.
        
        Args:
            search_results: List of search results
            
        Returns:
            Formatted string summarizing sources
        """
        if not search_results:
            return "No sources available."
        
        lines = [f"Sources ({len(search_results)} total):"]
        for i, result in enumerate(search_results, 1):
            date_str = f" ({result.published_date})" if result.published_date else ""
            lines.append(f"{i}. {result.title}{date_str}")
            lines.append(f"   URL: {result.url}")
        
        return "\n".join(lines)
    
    def identify_key_topics(
        self,
        text: str,
        max_topics: int = 5,
    ) -> list[str]:
        """
        Identify key topics/themes from text.
        
        Uses keyword extraction and grouping to identify main topics.
        
        Args:
            text: Text to analyze
            max_topics: Maximum number of topics to return
            
        Returns:
            List of identified topics
        """
        keywords = self.extract_keywords(text, top_n=20)
        
        # Group related keywords (simple approach)
        topics = []
        for word, count in keywords:
            if count >= 2:  # Only include words that appear multiple times
                topics.append(word)
                if len(topics) >= max_topics:
                    break
        
        return topics
    
    def calculate_word_count(self, text: str) -> int:
        """
        Calculate word count of text.
        
        Args:
            text: Text to count
            
        Returns:
            Word count
        """
        if not text:
            return 0
        return len(text.split())
    
    def truncate_text(
        self,
        text: str,
        max_length: int = 1000,
        suffix: str = "...",
    ) -> str:
        """
        Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)].rsplit(" ", 1)[0] + suffix


class ResearchDataProcessor:
    """
    Processor for combining and preparing research data for analysis.
    """
    
    def __init__(self):
        """Initialize the processor."""
        self.analyzer = TextAnalyzer()
        logger.debug("ResearchDataProcessor initialized")
    
    def combine_content(self, research_data: ResearchData) -> str:
        """
        Combine all content from research data into a single text.
        
        Args:
            research_data: Research data to process
            
        Returns:
            Combined content string
        """
        parts = []
        
        # Add topic
        parts.append(f"Topic: {research_data.topic}")
        parts.append("")
        
        # Add individual results
        for result in research_data.search_results:
            parts.append(f"## {result.title}")
            parts.append(f"Source: {result.url}")
            if result.published_date:
                parts.append(f"Date: {result.published_date}")
            parts.append(f"\n{result.content}\n")
        
        # Add researcher notes if available
        if research_data.researcher_notes:
            parts.append(f"\nResearcher Notes: {research_data.researcher_notes}")
        
        return "\n".join(parts)
    
    def prepare_for_analysis(
        self,
        research_data: ResearchData,
    ) -> dict:
        """
        Prepare research data for LLM analysis.
        
        Args:
            research_data: Research data to prepare
            
        Returns:
            Dictionary with prepared data and metadata
        """
        combined_content = self.combine_content(research_data)
        quality_score = self.analyzer.assess_data_quality(research_data)
        sentiment_score, sentiment_label = self.analyzer.calculate_sentiment_score(
            combined_content
        )
        keywords = self.analyzer.extract_keywords(combined_content)
        key_topics = self.analyzer.identify_key_topics(combined_content)
        numbers = self.analyzer.extract_numbers(combined_content)
        
        return {
            "topic": research_data.topic,
            "combined_content": combined_content,
            "sources_count": research_data.sources_count,
            "quality_score": quality_score,
            "preliminary_sentiment": sentiment_label,
            "sentiment_score": sentiment_score,
            "keywords": keywords,
            "key_topics": key_topics,
            "extracted_numbers": numbers,
            "word_count": self.analyzer.calculate_word_count(combined_content),
            "sources_summary": self.analyzer.summarize_sources(
                research_data.search_results
            ),
        }
    
    def format_for_llm(
        self,
        research_data: ResearchData,
        max_content_length: int = 8000,
    ) -> str:
        """
        Format research data for LLM consumption.
        
        Args:
            research_data: Research data to format
            max_content_length: Maximum content length
            
        Returns:
            Formatted string for LLM
        """
        prepared = self.prepare_for_analysis(research_data)
        
        # Truncate content if needed
        content = prepared["combined_content"]
        if len(content) > max_content_length:
            content = self.analyzer.truncate_text(content, max_content_length)
        
        formatted = f"""
## Research Data for Analysis

**Topic:** {prepared['topic']}
**Sources:** {prepared['sources_count']} sources found
**Data Quality Score:** {prepared['quality_score']:.2f}/1.00
**Preliminary Sentiment:** {prepared['preliminary_sentiment']}

### Key Topics Identified
{', '.join(prepared['key_topics']) if prepared['key_topics'] else 'No clear topics identified'}

### Top Keywords
{', '.join([f"{word} ({count})" for word, count in prepared['keywords'][:10]])}

### Research Content

{content}

### Sources
{prepared['sources_summary']}
"""
        return formatted.strip()


# =============================================================================
# Factory Functions
# =============================================================================

def create_text_analyzer() -> TextAnalyzer:
    """Create a TextAnalyzer instance."""
    return TextAnalyzer()


def create_data_processor() -> ResearchDataProcessor:
    """Create a ResearchDataProcessor instance."""
    return ResearchDataProcessor()


__all__ = [
    "TextAnalyzer",
    "ResearchDataProcessor",
    "create_text_analyzer",
    "create_data_processor",
]
