"""Test the agent with a few GAIA examples."""

import asyncio
import requests
from config import get_settings
from workflow import run_workflow

settings = get_settings()

def fetch_questions(count=3):
    """Fetch multiple questions from GAIA API."""
    url = f"{settings.api.gaia_api_url}/questions"
    print(f"Fetching questions from: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        all_questions = response.json()
        print(f"✓ Fetched {len(all_questions)} total questions")
        return all_questions[:count]
    except Exception as e:
        print(f"✗ Error fetching questions: {e}")
        return []

async def test_question(question_data, index):
    """Test a single question."""
    task_id = question_data.get("task_id", "unknown")
    question = question_data.get("question", "")
    level = question_data.get("Level", "unknown")
    ground_truth = question_data.get("Final answer", "N/A")
    
    print(f"\n{'='*80}")
    print(f"Question {index}")
    print(f"{'='*80}")
    print(f"Task ID: {task_id}")
    print(f"Level: {level}")
    print(f"Question: {question}")
    print(f"Expected Answer: {ground_truth}")
    print(f"\nRunning agent...")
    
    try:
        result = await run_workflow(
            question=question,
            task_id=task_id,
            use_structured_output=True,
            verbose=False
        )
        
        answer = result.get("answer", "No answer")
        elapsed = result.get("elapsed_time", 0)
        
        print(f"\n✓ Agent Answer: {answer}")
        print(f"⏱  Time: {elapsed:.2f}s")
        
        # Check if correct
        if str(answer).strip().lower() == str(ground_truth).strip().lower():
            print("✅ CORRECT - Exact match!")
            return True
        else:
            print("❌ INCORRECT - Answer differs")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("="*80)
    print("GAIA Agent Test - Running on 3 Examples")
    print("="*80)
    
    # Fetch questions
    questions = fetch_questions(count=3)
    
    if not questions:
        print("\n✗ Could not fetch questions. Exiting.")
        return
    
    # Test each question
    results = []
    for i, q in enumerate(questions, 1):
        correct = await test_question(q, i)
        results.append(correct)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total Questions: {len(results)}")
    print(f"Correct: {sum(results)}")
    print(f"Accuracy: {sum(results)/len(results)*100:.1f}%")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(main())


