"""
Specialist Agents for Agent Framework (Agent 06)

This module contains specialized agents for different domains:
- NLPAgent: Natural Language Processing tasks
- CodeAgent: Code analysis and generation
- DataAgent: Data processing and analysis
- ResearchAgent: Research and information gathering

Each specialist agent inherits from BaseAgent and provides domain-specific capabilities.
"""

import asyncio
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json

from app.core.base_agent import BaseAgent, AgentCapability
from app.core.message_bus import get_message_bus
from app.models.messaging import (
    TaskEnvelope, TaskResultEnvelope,
    create_task_result_envelope
)

logger = logging.getLogger(__name__)


class NLPAgent(BaseAgent):
    """
    Natural Language Processing Specialist Agent.

    Handles text analysis, sentiment analysis, summarization,
    language detection, and text processing tasks.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id=agent_id, agent_type="nlp_specialist", config=config)
        self.capabilities = [
            AgentCapability.NLP_PROCESSING,
            AgentCapability.TEXT_ANALYSIS,
            AgentCapability.SENTIMENT_ANALYSIS,
            AgentCapability.LANGUAGE_DETECTION
        ]
        self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']

    async def execute(self, task_envelope: TaskEnvelope) -> TaskResultEnvelope:
        """Execute NLP tasks."""
        task_data = task_envelope.payload
        operation = task_data.get("operation", "")

        try:
            if operation == "analyze_text":
                result = await self._analyze_text(task_data)
            elif operation == "sentiment_analysis":
                result = await self._sentiment_analysis(task_data)
            elif operation == "summarize_text":
                result = await self._summarize_text(task_data)
            elif operation == "detect_language":
                result = await self._detect_language(task_data)
            else:
                result = {"error": f"Unsupported NLP operation: {operation}"}

            return create_task_result_envelope(
                task_id=task_envelope.task_id,
                result=result,
                status="completed"
            )

        except Exception as e:
            logger.error(f"NLP task failed: {e}")
            return create_task_result_envelope(
                task_id=task_envelope.task_id,
                result=None,
                status="failed",
                error=str(e)
            )

    async def _analyze_text(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text for various metrics."""
        text = task_data.get("text", "")

        # Basic text analysis (would use NLP libraries in production)
        analysis = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "average_word_length": sum(len(word) for word in text.split()) / max(1, len(text.split())),
            "complexity_score": self._calculate_text_complexity(text)
        }

        return analysis

    async def _sentiment_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform sentiment analysis."""
        text = task_data.get("text", "")

        # Simple rule-based sentiment analysis (would use ML models in production)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'hate']

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, positive_count / max(1, len(words)))
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, negative_count / max(1, len(words)))
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }

    async def _summarize_text(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text summary."""
        text = task_data.get("text", "")
        max_length = task_data.get("max_length", 100)

        # Simple extractive summarization (would use advanced NLP in production)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Score sentences by position and length
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            position_score = 1.0 if i == 0 else (0.5 if i == len(sentences) - 1 else 0.3)
            length_score = min(1.0, len(sentence.split()) / 20)
            score = position_score + length_score
            scored_sentences.append((sentence, score))

        # Select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        selected_sentences = scored_sentences[:3]  # Top 3 sentences
        selected_sentences.sort(key=lambda x: sentences.index(x[0]))  # Maintain order

        summary = '. '.join(sentence for sentence, _ in selected_sentences)
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."

        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / max(1, len(text))
        }

    async def _detect_language(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect language of text."""
        text = task_data.get("text", "")

        # Simple language detection based on common words (would use proper NLP in production)
        language_patterns = {
            'en': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that'],
            'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es'],
            'fr': ['le', 'la', 'de', 'et', 'à', 'un', 'il', 'être'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das'],
            'it': ['il', 'la', 'di', 'e', 'a', 'un', 'è', 'per']
        }

        text_lower = text.lower()
        scores = {}

        for lang, words in language_patterns.items():
            score = sum(1 for word in words if word in text_lower)
            scores[lang] = score

        detected_lang = max(scores.items(), key=lambda x: x[1])
        confidence = detected_lang[1] / max(1, len(text.split()))

        return {
            "detected_language": detected_lang[0],
            "confidence": min(1.0, confidence * 2),  # Scale up for better results
            "all_scores": scores
        }

    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score."""
        words = text.split()
        if not words:
            return 0.0

        avg_word_length = sum(len(word) for word in words) / len(words)
        unique_words = len(set(word.lower() for word in words))
        lexical_diversity = unique_words / len(words)

        # Simple complexity formula
        complexity = (avg_word_length * 0.3) + (lexical_diversity * 0.7)
        return min(1.0, complexity)


class CodeAgent(BaseAgent):
    """
    Code Analysis and Generation Specialist Agent.

    Handles code review, generation, optimization, and analysis tasks.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id=agent_id, agent_type="code_specialist", config=config)
        self.capabilities = [
            AgentCapability.CODE_ANALYSIS,
            AgentCapability.CODE_GENERATION,
            AgentCapability.CODE_OPTIMIZATION,
            AgentCapability.CODE_REVIEW
        ]
        self.supported_languages = ['python', 'javascript', 'typescript', 'java', 'c++', 'go', 'rust']

    async def execute(self, task_envelope: TaskEnvelope) -> TaskResultEnvelope:
        """Execute code-related tasks."""
        task_data = task_envelope.payload
        operation = task_data.get("operation", "")

        try:
            if operation == "analyze_code":
                result = await self._analyze_code(task_data)
            elif operation == "generate_code":
                result = await self._generate_code(task_data)
            elif operation == "optimize_code":
                result = await self._optimize_code(task_data)
            elif operation == "review_code":
                result = await self._review_code(task_data)
            else:
                result = {"error": f"Unsupported code operation: {operation}"}

            return create_task_result_envelope(
                task_id=task_envelope.task_id,
                result=result,
                status="completed"
            )

        except Exception as e:
            logger.error(f"Code task failed: {e}")
            return create_task_result_envelope(
                task_id=task_envelope.task_id,
                result=None,
                status="failed",
                error=str(e)
            )

    async def _analyze_code(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for metrics and patterns."""
        code = task_data.get("code", "")
        language = task_data.get("language", "python")

        # Basic code analysis
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        analysis = {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "empty_lines": len(lines) - len(non_empty_lines),
            "language": language,
            "complexity_metrics": self._calculate_code_complexity(code, language),
            "quality_score": self._assess_code_quality(code, language)
        }

        return analysis

    async def _generate_code(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on specifications."""
        specification = task_data.get("specification", "")
        language = task_data.get("language", "python")

        # Template-based code generation (would use ML models in production)
        if "function" in specification.lower():
            code = self._generate_function_template(specification, language)
        elif "class" in specification.lower():
            code = self._generate_class_template(specification, language)
        else:
            code = f"# Generated code for: {specification}\n# Language: {language}\nprint('Hello, World!')"

        return {
            "generated_code": code,
            "language": language,
            "specification": specification,
            "confidence": 0.7  # Would be ML model confidence
        }

    async def _optimize_code(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize code for performance."""
        code = task_data.get("code", "")
        language = task_data.get("language", "python")

        # Basic optimization suggestions (would use advanced analysis in production)
        optimizations = []

        if language == "python":
            if "for i in range(len(" in code:
                optimizations.append("Use enumerate() instead of range(len())")
            if "print(" in code and "file=" not in code:
                optimizations.append("Consider using logging instead of print statements")

        return {
            "original_code": code,
            "optimizations": optimizations,
            "estimated_improvement": len(optimizations) * 0.05,  # 5% per optimization
            "language": language
        }

    async def _review_code(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for issues and improvements."""
        code = task_data.get("code", "")
        language = task_data.get("language", "python")

        issues = []
        suggestions = []

        # Basic code review rules
        if len(code.split('\n')) > 100:
            issues.append("File is quite long, consider splitting into smaller modules")

        if "TODO" in code or "FIXME" in code:
            issues.append("Found TODO/FIXME comments that should be addressed")

        if language == "python":
            if "import *" in code:
                issues.append("Avoid wildcard imports (import *)")
            if not any("if __name__ == '__main__':" in line for line in code.split('\n')):
                suggestions.append("Consider adding if __name__ == '__main__': guard")

        return {
            "issues": issues,
            "suggestions": suggestions,
            "severity_score": len(issues) * 0.1,  # 0.1 per issue
            "overall_rating": "good" if len(issues) == 0 else "needs_improvement",
            "language": language
        }

    def _calculate_code_complexity(self, code: str, language: str) -> Dict[str, Any]:
        """Calculate code complexity metrics."""
        lines = code.split('\n')

        # Cyclomatic complexity approximation
        keywords = {
            'python': ['if ', 'elif ', 'else:', 'for ', 'while ', 'def ', 'class '],
            'javascript': ['if ', 'else ', 'for ', 'while ', 'function ', 'class ']
        }

        complexity_keywords = keywords.get(language, [])
        complexity_score = 1  # Base complexity

        for line in lines:
            for keyword in complexity_keywords:
                if keyword in line:
                    complexity_score += 1

        return {
            "cyclomatic_complexity": complexity_score,
            "lines_of_code": len(lines),
            "complexity_rating": "low" if complexity_score < 10 else "medium" if complexity_score < 20 else "high"
        }

    def _assess_code_quality(self, code: str, language: str) -> float:
        """Assess overall code quality (0.0 to 1.0)."""
        score = 0.5  # Base score

        # Check for documentation
        if '"""' in code or '/*' in code or '//' in code:
            score += 0.1

        # Check for error handling
        if 'try:' in code or 'catch' in code or 'except' in code:
            score += 0.1

        # Check for reasonable length
        lines = len(code.split('\n'))
        if 10 <= lines <= 500:
            score += 0.1
        elif lines > 1000:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _generate_function_template(self, spec: str, language: str) -> str:
        """Generate function template."""
        if language == "python":
            return f'''def generated_function():
    """
    Generated function for: {spec}

    TODO: Implement the actual functionality
    """
    # Implementation goes here
    pass

    return None'''
        else:
            return f'// Generated function for: {spec}\nfunction generatedFunction() {{\n    // Implementation goes here\n\}}'

    def _generate_class_template(self, spec: str, language: str) -> str:
        """Generate class template."""
        if language == "python":
            return f'''class GeneratedClass:
    """
    Generated class for: {spec}
    """

    def __init__(self):
        """Initialize the class."""
        pass

    def example_method(self):
        """Example method - implement actual functionality."""
        return "Hello from generated class"'''
        else:
            return f'''// Generated class for: {spec}
class GeneratedClass {{
    constructor() {{
        // Implementation goes here
    }}

    exampleMethod() {{
        return "Hello from generated class";
    }}
}}'''


class DataAgent(BaseAgent):
    """
    Data Processing and Analysis Specialist Agent.

    Handles data cleaning, transformation, analysis, and visualization tasks.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id=agent_id, agent_type="data_specialist", config=config)
        self.capabilities = [
            AgentCapability.DATA_PROCESSING,
            AgentCapability.DATA_ANALYSIS,
            AgentCapability.DATA_VISUALIZATION,
            AgentCapability.STATISTICAL_ANALYSIS
        ]

    async def execute(self, task_envelope: TaskEnvelope) -> TaskResultEnvelope:
        """Execute data-related tasks."""
        task_data = task_envelope.payload
        operation = task_data.get("operation", "")

        try:
            if operation == "analyze_dataset":
                result = await self._analyze_dataset(task_data)
            elif operation == "clean_data":
                result = await self._clean_data(task_data)
            elif operation == "transform_data":
                result = await self._transform_data(task_data)
            elif operation == "generate_statistics":
                result = await self._generate_statistics(task_data)
            else:
                result = {"error": f"Unsupported data operation: {operation}"}

            return create_task_result_envelope(
                task_id=task_envelope.task_id,
                result=result,
                status="completed"
            )

        except Exception as e:
            logger.error(f"Data task failed: {e}")
            return create_task_result_envelope(
                task_id=task_envelope.task_id,
                result=None,
                status="failed",
                error=str(e)
            )

    async def _analyze_dataset(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dataset structure and characteristics."""
        data = task_data.get("data", [])

        if not isinstance(data, list):
            return {"error": "Data must be a list"}

        analysis = {
            "total_records": len(data),
            "data_types": self._analyze_data_types(data),
            "missing_values": self._count_missing_values(data),
            "duplicate_records": len(data) - len(set(str(item) for item in data)),
            "basic_statistics": self._calculate_basic_stats(data)
        }

        return analysis

    async def _clean_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and preprocess data."""
        data = task_data.get("data", [])

        if not isinstance(data, list):
            return {"error": "Data must be a list"}

        # Basic data cleaning operations
        cleaned_data = []
        cleaning_operations = []

        for item in data:
            if item is None or item == "":
                cleaning_operations.append("removed_null_empty")
                continue

            # Remove duplicates (simplified)
            if item not in cleaned_data:
                cleaned_data.append(item)
                cleaning_operations.append("kept_unique")
            else:
                cleaning_operations.append("removed_duplicate")

        return {
            "original_count": len(data),
            "cleaned_count": len(cleaned_data),
            "cleaned_data": cleaned_data,
            "operations_performed": cleaning_operations
        }

    async def _transform_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to specifications."""
        data = task_data.get("data", [])
        transformation = task_data.get("transformation", "normalize")

        if not isinstance(data, list):
            return {"error": "Data must be a list"}

        transformed_data = []

        if transformation == "normalize":
            # Simple normalization (would use proper statistical methods in production)
            if data:
                min_val = min(data) if all(isinstance(x, (int, float)) for x in data) else 0
                max_val = max(data) if all(isinstance(x, (int, float)) for x in data) else 1
                range_val = max_val - min_val

                if range_val > 0:
                    transformed_data = [(x - min_val) / range_val for x in data]
                else:
                    transformed_data = data

        elif transformation == "standardize":
            # Simple standardization
            if data and all(isinstance(x, (int, float)) for x in data):
                mean_val = sum(data) / len(data)
                std_val = (sum((x - mean_val) ** 2 for x in data) / len(data)) ** 0.5

                if std_val > 0:
                    transformed_data = [(x - mean_val) / std_val for x in data]
                else:
                    transformed_data = data

        return {
            "original_data": data,
            "transformed_data": transformed_data,
            "transformation_applied": transformation,
            "transformation_success": len(transformed_data) == len(data)
        }

    async def _generate_statistics(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistical analysis of data."""
        data = task_data.get("data", [])

        if not isinstance(data, list) or not data:
            return {"error": "Valid data list required"}

        # Filter to numeric data
        numeric_data = [x for x in data if isinstance(x, (int, float))]

        if not numeric_data:
            return {"error": "No numeric data found for statistical analysis"}

        # Calculate statistics
        sorted_data = sorted(numeric_data)
        n = len(sorted_data)

        statistics = {
            "count": n,
            "mean": sum(numeric_data) / n,
            "median": sorted_data[n // 2] if n % 2 == 1 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2,
            "minimum": min(numeric_data),
            "maximum": max(numeric_data),
            "range": max(numeric_data) - min(numeric_data),
            "variance": sum((x - sum(numeric_data) / n) ** 2 for x in numeric_data) / n,
            "standard_deviation": (sum((x - sum(numeric_data) / n) ** 2 for x in numeric_data) / n) ** 0.5
        }

        # Quartiles
        statistics["q1"] = sorted_data[n // 4]
        statistics["q3"] = sorted_data[3 * n // 4]

        return statistics

    def _analyze_data_types(self, data: List[Any]) -> Dict[str, int]:
        """Analyze data types in the dataset."""
        type_counts = {}

        for item in data:
            type_name = type(item).__name__
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return type_counts

    def _count_missing_values(self, data: List[Any]) -> int:
        """Count missing/null values in data."""
        return sum(1 for item in data if item is None or item == "" or str(item).lower() in ['null', 'none', 'nan'])

    def _calculate_basic_stats(self, data: List[Any]) -> Dict[str, Any]:
        """Calculate basic statistics for the dataset."""
        stats = {
            "total_items": len(data),
            "unique_items": len(set(str(item) for item in data)),
            "has_duplicates": len(data) != len(set(str(item) for item in data))
        }

        return stats


class ResearchAgent(BaseAgent):
    """
    Research and Information Gathering Specialist Agent.

    Handles research tasks, information synthesis, knowledge discovery,
    and hypothesis generation.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id=agent_id, agent_type="research_specialist", config=config)
        self.capabilities = [
            AgentCapability.RESEARCH,
            AgentCapability.INFORMATION_SYNTHESIS,
            AgentCapability.KNOWLEDGE_DISCOVERY,
            AgentCapability.HYPOTHESIS_GENERATION
        ]

    async def execute(self, task_envelope: TaskEnvelope) -> TaskResultEnvelope:
        """Execute research-related tasks."""
        task_data = task_envelope.payload
        operation = task_data.get("operation", "")

        try:
            if operation == "research_topic":
                result = await self._research_topic(task_data)
            elif operation == "synthesize_information":
                result = await self._synthesize_information(task_data)
            elif operation == "generate_hypotheses":
                result = await self._generate_hypotheses(task_data)
            elif operation == "analyze_trends":
                result = await self._analyze_trends(task_data)
            else:
                result = {"error": f"Unsupported research operation: {operation}"}

            return create_task_result_envelope(
                task_id=task_envelope.task_id,
                result=result,
                status="completed"
            )

        except Exception as e:
            logger.error(f"Research task failed: {e}")
            return create_task_result_envelope(
                task_id=task_envelope.task_id,
                result=None,
                status="failed",
                error=str(e)
            )

    async def _research_topic(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research a given topic and gather information."""
        topic = task_data.get("topic", "")
        depth = task_data.get("depth", "basic")

        # Simulate research process (would use web search, APIs, etc. in production)
        research_results = {
            "topic": topic,
            "depth": depth,
            "key_findings": [
                f"Primary aspects of {topic}",
                f"Current trends in {topic}",
                f"Related concepts to {topic}"
            ],
            "sources": [
                f"Academic papers on {topic}",
                f"Industry reports about {topic}",
                f"Expert opinions regarding {topic}"
            ],
            "confidence_score": 0.8,
            "information_completeness": 0.7
        }

        return research_results

    async def _synthesize_information(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multiple sources of information."""
        sources = task_data.get("sources", [])
        topic = task_data.get("topic", "")

        # Simulate information synthesis
        synthesis = {
            "topic": topic,
            "sources_analyzed": len(sources),
            "key_insights": [
                f"Common themes across {len(sources)} sources",
                f"Conflicting viewpoints identified",
                f"Gaps in current knowledge"
            ],
            "consensus_points": [
                f"Agreed-upon facts about {topic}",
                f"Established best practices",
                f"Industry standards"
            ],
            "controversial_points": [
                f"Ongoing debates in {topic}",
                f"Emerging vs established views",
                f"Unresolved questions"
            ],
            "synthesis_quality": "high" if len(sources) > 3 else "moderate"
        }

        return synthesis

    async def _generate_hypotheses(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate research hypotheses based on available data."""
        data = task_data.get("data", {})
        domain = task_data.get("domain", "general")

        # Simulate hypothesis generation
        hypotheses = [
            {
                "hypothesis": f"Increased {domain} efficiency correlates with system optimization",
                "evidence_strength": "moderate",
                "testability": "high",
                "impact": "significant"
            },
            {
                "hypothesis": f"Meta-learning approaches improve {domain} performance over time",
                "evidence_strength": "strong",
                "testability": "medium",
                "impact": "high"
            },
            {
                "hypothesis": f"Parallel processing reduces {domain} task completion time",
                "evidence_strength": "moderate",
                "testability": "high",
                "impact": "moderate"
            }
        ]

        return {
            "domain": domain,
            "hypotheses_generated": len(hypotheses),
            "hypotheses": hypotheses,
            "generation_method": "pattern_analysis",
            "confidence_level": "medium"
        }

    async def _analyze_trends(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in data or research areas."""
        data = task_data.get("data", [])
        time_period = task_data.get("time_period", "recent")

        # Simulate trend analysis
        trends = {
            "time_period": time_period,
            "data_points_analyzed": len(data),
            "identified_trends": [
                {
                    "trend": "Increasing complexity in processing requirements",
                    "direction": "upward",
                    "strength": "strong",
                    "timeframe": time_period
                },
                {
                    "trend": "Growing adoption of meta-learning approaches",
                    "direction": "upward",
                    "strength": "moderate",
                    "timeframe": time_period
                },
                {
                    "trend": "Shift toward parallel and distributed processing",
                    "direction": "upward",
                    "strength": "strong",
                    "timeframe": time_period
                }
            ],
            "trend_confidence": 0.75,
            "prediction_accuracy": 0.8
        }

        return trends
