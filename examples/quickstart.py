"""Run with: python examples/quickstart.py"""
import asyncio
from pathlib import Path

import engram

engram.configure(Path.home() / ".engram-quickstart")


async def main():
    print("Storing memories...")
    await engram.remember(
        "Marie Curie was born in Warsaw, Poland in 1867.",
        dataset="science",
    )
    await engram.remember(
        "Marie Curie won the Nobel Prize in Physics in 1903 and Chemistry in 1911.",
        dataset="science",
    )
    await engram.remember(
        "Warsaw is the capital and largest city of Poland.",
        dataset="geography",
    )

    print("\nRecalling about Marie Curie...")
    results = await engram.recall(
        "Tell me about Marie Curie's achievements",
        datasets=["science"],
    )
    for r in results:
        print(f"  [{r['strength']:.2f}] {r['text']}")
        if r["related"]:
            print(f"    Related: {r['related']}")

    print("\nImproving memory with new info...")
    await engram.improve(
        "Marie Curie was the first woman to win a Nobel Prize.",
        dataset="science",
    )

    print("\nPruning faded memories (threshold=0.01)...")
    removed = await engram.prune(dataset="science", threshold=0.01)
    print(f"  Removed {removed} weak memories")

    print("\nForgetting geography dataset...")
    await engram.forget(dataset="geography")
    results = await engram.recall("Warsaw", datasets=["geography"])
    print(f"  Results after forget: {len(results)} (expected 0)")


asyncio.run(main())
