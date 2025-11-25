"""Quick test script to verify the agent setup."""

import asyncio
import sys
from test_agent import fetch_random_question, test_single_question

async def main():
    print("=" * 80)
    print("GAIA Agent Quick Test")
    print("=" * 80)
    
    # Test 1: Fetch a random question
    print("\n[Test 1] Fetching a random question from GAIA API...")
    question_data = fetch_random_question()
    
    if question_data:
        print(f"✓ Successfully fetched question!")
        print(f"  Task ID: {question_data.get('task_id', 'N/A')}")
        print(f"  Level: {question_data.get('Level', 'N/A')}")
        print(f"  Question: {question_data.get('question', 'N/A')[:100]}...")
        print(f"  Ground Truth: {question_data.get('Final answer', 'N/A')}")
        
        # Test 2: Run agent on the question
        print("\n[Test 2] Running agent on the question...")
        print("(This may take a while...)")
        await test_single_question(verbose=False)
    else:
        print("✗ Failed to fetch question from GAIA API")
        print("  Check your internet connection and API endpoint")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())


