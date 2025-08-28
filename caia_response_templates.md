# Caia Response Templates

## Sentinel Alert → Reflex
- Title: 센티넬 조건 감지
- Body: ΔK200 {value}%, 레벨 {level}, 트리거 {trigger}. Hedge/Reflex 판단 루프 진입.

## Memory ERSP
```json
{
  "type": "strategy",
  "actor": "Caia",
  "importance": "high",
  "content": "{summary}",
  "metadata": {
    "ersp": {
      "event": "{event}",
      "interpretation": "{interpretation}",
      "lesson": "{lesson}",
      "if_then": "{if_then}"
    }
  }
}
```
