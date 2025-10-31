"""Topic Taxonomy - Hierarchical content categorization system."""

from dataclasses import dataclass
from typing import Dict, List, Set
from enum import Enum


class SafetyCategory(str, Enum):
    """Content safety ratings."""
    G = "G"                    # General audiences
    PG = "PG"                  # Parental guidance suggested
    PG_13 = "PG_13"           # Parents strongly cautioned
    R = "R"                    # Restricted
    ADULT_CONTENT = "adult_content"  # Adult/explicit content


@dataclass
class TopicCategory:
    """Topic category definition."""
    name: str
    topics: List[str]
    description: str
    safety_level: SafetyCategory = SafetyCategory.G


# Core topic taxonomy
TOPIC_CATEGORIES = {
    "financial": TopicCategory(
        name="financial",
        topics=["payment", "transaction", "billing", "refund", "invoice", "banking", "credit", "loan"],
        description="Financial transactions and monetary operations",
        safety_level=SafetyCategory.PG
    ),
    
    "privacy": TopicCategory(
        name="privacy", 
        topics=["pii", "phi", "personal_data", "medical_record", "ssn", "credit_card", "address", "phone"],
        description="Personal and private information",
        safety_level=SafetyCategory.PG_13
    ),
    
    "healthcare": TopicCategory(
        name="healthcare",
        topics=["medical", "healthcare", "patient", "diagnosis", "treatment", "prescription", "hospital"],
        description="Medical and healthcare related content",
        safety_level=SafetyCategory.PG
    ),
    
    "content_safety": TopicCategory(
        name="content_safety",
        topics=["adult", "violence", "illegal", "hate_speech", "harassment", "discrimination"],
        description="Potentially harmful or inappropriate content",
        safety_level=SafetyCategory.R
    ),
    
    "business": TopicCategory(
        name="business",
        topics=["recipe", "cooking", "automotive", "legal", "education", "travel", "entertainment"],
        description="General business and informational content",
        safety_level=SafetyCategory.G
    ),
    
    "system": TopicCategory(
        name="system",
        topics=["admin", "configuration", "deployment", "security", "database", "api", "infrastructure"],
        description="System administration and technical operations",
        safety_level=SafetyCategory.PG_13
    )
}


class TopicTaxonomy:
    """Manage topic categorization and validation."""
    
    def __init__(self):
        self.categories = TOPIC_CATEGORIES
        self._topic_to_category = self._build_topic_map()
    
    def _build_topic_map(self) -> Dict[str, str]:
        """Build reverse mapping from topic to category."""
        topic_map = {}
        for category_name, category in self.categories.items():
            for topic in category.topics:
                topic_map[topic] = category_name
        return topic_map
    
    def get_all_topics(self) -> List[str]:
        """Get all available topics."""
        topics = []
        for category in self.categories.values():
            topics.extend(category.topics)
        return sorted(topics)
    
    def get_category_topics(self, category: str) -> List[str]:
        """Get topics for a specific category."""
        if category in self.categories:
            return self.categories[category].topics
        return []
    
    def get_topic_category(self, topic: str) -> str:
        """Get category for a specific topic."""
        return self._topic_to_category.get(topic, "unknown")
    
    def validate_topics(self, topics: List[str]) -> Dict[str, List[str]]:
        """Validate topics and return categorized results."""
        result = {
            "valid": [],
            "invalid": [],
            "categories": []
        }
        
        for topic in topics:
            if topic in self._topic_to_category:
                result["valid"].append(topic)
                category = self._topic_to_category[topic]
                if category not in result["categories"]:
                    result["categories"].append(category)
            else:
                result["invalid"].append(topic)
        
        return result
    
    def get_safety_level(self, topics: List[str]) -> SafetyCategory:
        """Determine overall safety level for a list of topics."""
        max_level = SafetyCategory.G
        
        for topic in topics:
            category_name = self.get_topic_category(topic)
            if category_name in self.categories:
                category_level = self.categories[category_name].safety_level
                if category_level.value > max_level.value:
                    max_level = category_level
        
        return max_level
    
    def format_taxonomy(self) -> str:
        """Format taxonomy as readable text for LLM guidance."""
        output = "# Available Topic Categories\n\n"
        
        for category_name, category in self.categories.items():
            output += f"## {category_name.title()}\n"
            output += f"**Description**: {category.description}\n"
            output += f"**Safety Level**: {category.safety_level.value}\n"
            output += f"**Topics**: {', '.join(category.topics)}\n\n"
        
        return output
    
    def get_topic_guidance(self) -> str:
        """Get guidance text for client LLM topic extraction."""
        return f"""
**Topic Selection Guidelines:**

When converting natural language to ICP, analyze the request and select relevant topics from these categories:

{self.format_taxonomy()}

**Selection Rules:**
1. **Be Comprehensive**: Include ALL relevant topics from the request
2. **Privacy Detection**: Always include privacy topics (pii, phi) if personal information is mentioned
3. **Safety First**: Include content_safety topics if inappropriate content is detected
4. **Multiple Categories**: A request can span multiple categories (e.g., "payment" + "pii")

**Examples:**
- "make a payment to robert lee of 50$" → topics: ["payment", "pii"]
- "give me a recipe for pasta" → topics: ["recipe", "cooking"]
- "show patient medical records" → topics: ["phi", "medical_record", "healthcare"]
- "configure admin database settings" → topics: ["admin", "configuration", "database"]

**Safety Categories:**
- G: General content, safe for all users
- PG: May need parental guidance
- PG_13: Parents strongly cautioned
- R: Restricted content
- adult_content: Explicit/adult content
"""


# Global taxonomy instance
taxonomy = TopicTaxonomy()