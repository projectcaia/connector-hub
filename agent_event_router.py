from typing import Dict, Any

# Example helper to branch events to subscribers (future: /subscribe)
def match_subscription(evt: Dict[str, Any], sub: Dict[str, Any]) -> bool:
    for key in ("event", "trigger", "level", "source"):
        if key in sub and evt.get(key) != sub[key]:
            return False
    return True
