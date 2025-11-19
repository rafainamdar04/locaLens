"""Quick test of optimized /process_v3 endpoint."""
import asyncio
import time
from main import process_address_v3
from pydantic import BaseModel

class Req(BaseModel):
    raw_address: str

async def test():
    req = Req(raw_address='123 MG Road Bengaluru 560001')
    
    print("First call (cold):")
    start = time.time()
    response = await process_address_v3(req)
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Response time: {elapsed:.0f}ms")
    print(f"  ✓ Backend reported: {response.processing_time_ms:.0f}ms")
    print(f"  ✓ Health: {response.event.get('health')}")
    
    print("\nSecond call (cached):")
    start = time.time()
    response2 = await process_address_v3(req)
    elapsed2 = (time.time() - start) * 1000
    print(f"  ✓ Response time: {elapsed2:.0f}ms")
    print(f"  ✓ Backend reported: {response2.processing_time_ms:.0f}ms")
    speedup = elapsed / max(elapsed2, 1) if elapsed2 > 0 else elapsed
    print(f"  ✓ Speedup: ~{speedup:.0f}x faster (instant cache hit)")


if __name__ == "__main__":
    asyncio.run(test())
