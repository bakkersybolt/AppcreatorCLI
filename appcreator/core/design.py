"""The parts of the design (.docs/ontwerp/) written by the brainstorm-architect skill."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class OntwerpDeel:
    key: str
    slug: str
    titel: str
    alleen_frontend: bool = False


ONTWERP_DELEN = [
    OntwerpDeel("doel", "doel", "Doel"),
    OntwerpDeel("stromen", "gebruikers-en-stromen", "Gebruikers en stromen"),
    OntwerpDeel("datamodel", "datamodel", "Datamodel"),
    OntwerpDeel("api", "api-en-toegang", "API en toegang"),
    OntwerpDeel("schermen", "schermen", "Schermen", alleen_frontend=True),
    OntwerpDeel("navigatie", "navigatie-en-uitstraling", "Navigatie en uitstraling", alleen_frontend=True),
    OntwerpDeel("scope", "randvoorwaarden-en-scope", "Randvoorwaarden en scope"),
]


def ontwerp_context(frontend: bool) -> Dict[str, Any]:
    """Numbered design parts for this stack; the build order is the round after the last part."""
    delen: List[Dict[str, Any]] = []
    for deel in ONTWERP_DELEN:
        if deel.alleen_frontend and not frontend:
            continue
        nr = len(delen) + 1
        delen.append({
            "key": deel.key,
            "nr": nr,
            "titel": deel.titel,
            "bestand": f"{nr:02d}-{deel.slug}.md",
        })
    return {
        "ontwerp_delen": delen,
        "ontwerp": {d["key"]: d for d in delen},
        "ronde_bouw": len(delen) + 1,
    }
