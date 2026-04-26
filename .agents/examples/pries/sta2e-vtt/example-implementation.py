"""
Example implementation produced by @pries-make for STA-001 Task 1.

File: app/services/broadcast.py
Mode: tdd (driven by tests in example-tests.py)

Verification:
  Command: uv run pytest tests/services/test_broadcast.py -q
  Exit code: 0
  Excerpt: 5 passed in 0.32s

Per-criterion results:
- AC-1 (subscriber lifecycle): PASS (test_subscriber_added_on_connect,
  test_subscriber_removed_on_disconnect)
- AC-2 (broadcast fan-out): PASS (test_broadcast_reaches_all_subscribers)
- AC-2/NFR-PERF-002 (latency): PASS (test_broadcast_latency_under_200ms)
- Resilience: PASS (test_slow_consumer_does_not_block_fanout)
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class Broadcaster:
    """In-memory per-scene WebSocket fan-out with bounded send timeout.

    Constraints inherited from STA-001 plan:
    - Latency <200 ms for 50 subscribers (NFR-PERF-002).
    - Slow consumers must not block other subscribers; evict after timeout.
    """

    def __init__(self, send_timeout_ms: int = 250) -> None:
        self._subs: dict[str, set[asyncio.Queue[Any]]] = defaultdict(set)
        self._send_timeout = send_timeout_ms / 1000.0

    async def connect(self, scene_id: str, subscriber: asyncio.Queue[Any]) -> None:
        self._subs[scene_id].add(subscriber)

    async def disconnect(self, scene_id: str, subscriber: asyncio.Queue[Any]) -> None:
        self._subs[scene_id].discard(subscriber)

    def subscriber_count(self, scene_id: str) -> int:
        return len(self._subs.get(scene_id, set()))

    async def broadcast(self, scene_id: str, payload: Any) -> None:
        """Fan out payload to all subscribers; evict any that exceed timeout."""
        targets = list(self._subs.get(scene_id, set()))
        if not targets:
            return

        async def _send_one(q: asyncio.Queue[Any]) -> tuple[asyncio.Queue[Any], bool]:
            try:
                await asyncio.wait_for(q.put(payload), timeout=self._send_timeout)
                return q, True
            except (asyncio.TimeoutError, asyncio.QueueFull):
                return q, False

        results = await asyncio.gather(*[_send_one(q) for q in targets])
        for q, ok in results:
            if not ok:
                self._subs[scene_id].discard(q)
