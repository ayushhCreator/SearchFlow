"""
Source Credibility Scoring

Assigns credibility scores to sources based on domain reputation.
Higher scores indicate more trustworthy sources.

Score Tiers:
- 0.95: Official documentation, academic sources
- 0.85: Reputable tech blogs, major publications
- 0.70: Community wikis, Stack Overflow
- 0.60: General websites
- 0.40: User-generated content without moderation
- 0.20: Known low-quality or spam domains
"""

import logging
from typing import Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Domain reputation database
# Format: domain_pattern -> (score, category)
DOMAIN_SCORES: Dict[str, tuple[float, str]] = {
    # Official Documentation (0.95)
    "docs.python.org": (0.95, "official_docs"),
    "fastapi.tiangolo.com": (0.95, "official_docs"),
    "react.dev": (0.95, "official_docs"),
    "nextjs.org": (0.95, "official_docs"),
    "vuejs.org": (0.95, "official_docs"),
    "angular.io": (0.95, "official_docs"),
    "kubernetes.io": (0.95, "official_docs"),
    "docker.com": (0.95, "official_docs"),
    "pytorch.org": (0.95, "official_docs"),
    "tensorflow.org": (0.95, "official_docs"),
    "developer.mozilla.org": (0.95, "official_docs"),
    "learn.microsoft.com": (0.95, "official_docs"),
    "cloud.google.com": (0.95, "official_docs"),
    "aws.amazon.com": (0.95, "official_docs"),
    "redis.io": (0.95, "official_docs"),
    "postgresql.org": (0.95, "official_docs"),
    "mongodb.com": (0.95, "official_docs"),
    "djangoproject.com": (0.95, "official_docs"),
    "flask.palletsprojects.com": (0.95, "official_docs"),
    "golang.org": (0.95, "official_docs"),
    "rust-lang.org": (0.95, "official_docs"),
    # Academic & Research (0.93)
    "arxiv.org": (0.93, "academic"),
    "github.com": (0.90, "code_repository"),
    "gitlab.com": (0.90, "code_repository"),
    # Reputable Tech Publications (0.85)
    "medium.com": (0.70, "blog_platform"),
    "dev.to": (0.75, "tech_community"),
    "hashnode.dev": (0.75, "tech_community"),
    "freecodecamp.org": (0.85, "educational"),
    "realpython.com": (0.88, "tech_tutorial"),
    "digitalocean.com": (0.85, "tech_tutorial"),
    "tutorialspoint.com": (0.70, "tech_tutorial"),
    "geeksforgeeks.org": (0.72, "tech_tutorial"),
    "w3schools.com": (0.65, "tech_tutorial"),
    "baeldung.com": (0.85, "tech_tutorial"),
    "datacamp.com": (0.82, "educational"),
    # Community & Q&A (0.70-0.75)
    "stackoverflow.com": (0.78, "qa_community"),
    "stackexchange.com": (0.75, "qa_community"),
    "reddit.com": (0.55, "social_community"),
    "quora.com": (0.50, "qa_community"),
    # News & Publications (0.80)
    "techcrunch.com": (0.80, "tech_news"),
    "wired.com": (0.80, "tech_news"),
    "arstechnica.com": (0.82, "tech_news"),
    "theverge.com": (0.78, "tech_news"),
    "hackernews.com": (0.75, "tech_news"),
    # Wikipedia (0.72 - good overview but verify)
    "wikipedia.org": (0.72, "encyclopedia"),
    "en.wikipedia.org": (0.72, "encyclopedia"),
    # Low Quality Indicators (0.30-0.40)
    "blogspot.com": (0.40, "personal_blog"),
    "wordpress.com": (0.45, "personal_blog"),
}

# Trusted TLD patterns
TRUSTED_TLDS = {
    ".edu": 0.90,
    ".gov": 0.92,
    ".org": 0.70,  # Base, can be overridden by domain
}

# Low quality indicators in domain
LOW_QUALITY_PATTERNS = [
    "spam",
    "ads",
    "click",
    "free-",
    "cheap-",
    "-generator",
    "online-tool",
]


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def get_credibility_score(url: str) -> tuple[float, str]:
    """
    Get credibility score for a URL.

    Returns:
        Tuple of (score, category)
        - score: 0.0 to 1.0
        - category: String describing the source type
    """
    if not url:
        return (0.5, "unknown")

    domain = get_domain(url)
    if not domain:
        return (0.5, "unknown")

    # Check exact domain match
    if domain in DOMAIN_SCORES:
        return DOMAIN_SCORES[domain]

    # Check if domain ends with a known domain (subdomain support)
    for known_domain, (score, category) in DOMAIN_SCORES.items():
        if domain.endswith(f".{known_domain}") or domain == known_domain:
            return (score, category)

    # Check trusted TLDs
    for tld, score in TRUSTED_TLDS.items():
        if domain.endswith(tld):
            return (score, f"trusted_tld_{tld}")

    # Check low quality patterns
    for pattern in LOW_QUALITY_PATTERNS:
        if pattern in domain:
            return (0.30, "low_quality")

    # Default score for unknown domains
    return (0.55, "general")


def enrich_with_credibility(sources: list[dict]) -> list[dict]:
    """
    Enrich source list with credibility scores.

    Args:
        sources: List of source dicts with 'url' key

    Returns:
        Same list with added 'credibility_score' and 'credibility_category' keys
    """
    enriched = []
    for source in sources:
        url = source.get("url", "")
        score, category = get_credibility_score(url)
        enriched.append(
            {
                **source,
                "credibility_score": score,
                "credibility_category": category,
            }
        )

    logger.debug(f"Enriched {len(sources)} sources with credibility scores")
    return enriched


def sort_by_credibility(sources: list[dict], descending: bool = True) -> list[dict]:
    """
    Sort sources by credibility score.

    Args:
        sources: List of source dicts with 'credibility_score' key
        descending: If True, highest scores first

    Returns:
        Sorted list
    """
    return sorted(
        sources,
        key=lambda x: x.get("credibility_score", 0.5),
        reverse=descending,
    )
