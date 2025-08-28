from typing import Dict, Any

def build_ersp(row: Dict[str, Any]) -> Dict[str, str]:
    event = f"{row.get('source')} {row.get('event')} 전달"
    interpretation = "ConnectorHub를 통해 Caia 판단 루프로 유입 가능한 요약 이벤트."
    lesson = "외부 자동화도 전략 흐름에 무손실로 통합 가능."
    if_then = "ΔK200 ≤ -1.5% 등 조건 포함 시 Hedge/Reflex 판단 트리거."
    return {
        "event": event,
        "interpretation": interpretation,
        "lesson": lesson,
        "if_then": if_then
    }
