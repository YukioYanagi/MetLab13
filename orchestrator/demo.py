from __future__ import annotations

import asyncio
from collections import Counter
from datetime import date

from orchestrator.config import load_settings
from orchestrator.logging_config import configure_logging
from orchestrator.models import SearchRoomsRequest
from orchestrator.service import HotelOrchestrator


async def main() -> None:
    settings = load_settings()
    logger = configure_logging("orchestrator", settings.log_dir, settings.log_level)
    orchestrator = HotelOrchestrator(settings=settings, logger=logger)
    await orchestrator.connect()

    try:
        requests = [
            SearchRoomsRequest(
                city="Moscow",
                check_in=date(2026, 6, 12),
                check_out=date(2026, 6, 14),
                guests=2,
                rooms=1,
                max_price=220,
            )
            for _ in range(8)
        ]

        results = await asyncio.gather(
            *(orchestrator.search_available_rooms(request) for request in requests),
            return_exceptions=True,
        )

        distribution = Counter()
        for result in results:
            if isinstance(result, Exception):
                print(f"ERROR: {result}")
                continue
            distribution[result.agent_id] += 1
            print(
                f"request_id={result.request_id} agent_id={result.agent_id} "
                f"rooms={len(result.available_rooms)} handled_tasks={result.handled_tasks}"
            )

        print("Load balancing distribution:")
        for agent_id, count in distribution.items():
            print(f"  {agent_id}: {count}")
    finally:
        await orchestrator.close()


if __name__ == "__main__":
    asyncio.run(main())
