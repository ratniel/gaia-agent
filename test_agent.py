"""
Enhanced testing script with new configuration and structured outputs.
"""

import os
import sys
import asyncio
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

from workflow import run_workflow
from config import get_settings
from models.questions import GAIAQuestion, GAIAResult

# Get settings
settings = get_settings()


def fetch_random_question() -> Optional[Dict]:
    """Fetch a single random question from GAIA API."""
    try:
        url = f"{settings.api.gaia_api_url}/random-question"
        print(f"Fetching random question from: {url}")
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        question_data = response.json()
        return question_data
    
    except Exception as e:
        print(f"Error fetching random question: {e}")
        return None


def fetch_all_questions() -> Optional[List[Dict]]:
    """Fetch all questions from GAIA API."""
    try:
        url = f"{settings.api.gaia_api_url}/questions"
        print(f"Fetching all questions from: {url}")
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        questions_data = response.json()
        return questions_data
    
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return None


async def test_single_question(verbose: bool = True):
    """Test the agent on a single random question."""
    print("\n" + "="*80)
    print("SINGLE QUESTION TEST MODE - Enhanced Version")
    print("="*80 + "\n")
    
    # Fetch a random question
    question_data = fetch_random_question()
    
    if not question_data:
        print("Failed to fetch question. Exiting.")
        return
    
    # Parse with Pydantic model
    try:
        question_obj = GAIAQuestion(**question_data)
    except Exception as e:
        print(f"Warning: Could not parse question with Pydantic: {e}")
        question_obj = None
    
    # Extract details
    task_id = question_obj.task_id
    question = question_obj.question
    level = question_obj.level
    ground_truth = question_data.get("ground_truth", None)
    
    print(f"Task ID: {task_id}")
    print(f"Level: {level}")
    print(f"\nQuestion:\n{question}\n")
    print("-" * 80)
    
    # Run the agent
    print("\nRunning enhanced agent with structured outputs...\n")
    start_time = datetime.now()
    
    try:
        result = await run_workflow(
            question=question,
            task_id=task_id,
            use_structured_output=True,
            verbose=verbose
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Extract answer
        answer = result.get("answer", "No answer")
        
        print("\n" + "-" * 80)
        print(f"\n✓ Agent Answer: {answer}")
        print(f"\n⏱  Time taken: {duration:.2f} seconds")
        
        # Compare with ground truth if available
        if ground_truth:
            print(f"\n📋 Ground Truth: {ground_truth}")
            
            # Simple comparison
            if str(answer).strip().lower() == str(ground_truth).strip().lower():
                print("\n✅ EXACT MATCH! Answer matches ground truth.")
            else:
                print("\n❌ NO MATCH. Answer differs from ground truth.")
                print(f"   Similarity check needed for partial credit.")
        
        # Show any errors
        if "error" in result:
            print(f"\n⚠️  Error occurred: {result['error']}")
        
    except Exception as e:
        print(f"\n✗ Error running agent: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80 + "\n")


async def test_batch_questions(
    num_questions: int = 5,
    verbose: bool = False
):
    """Test the agent on multiple questions."""
    print("\n" + "="*80)
    print(f"BATCH TEST MODE - Testing {num_questions} questions")
    print("="*80 + "\n")
    
    # Fetch all questions
    all_questions = fetch_all_questions()
    
    if not all_questions:
        print("Failed to fetch questions. Exiting.")
        return
    
    print(f"Total questions available: {len(all_questions)}")
    
    # Limit to requested number
    questions_to_test = all_questions[:num_questions]
    
    results = []
    correct_count = 0
    total_time = 0
    
    for i, question_data in enumerate(questions_to_test, 1):
        task_id = question_data.get("task_id", "unknown")
        question = question_data.get("question", "")
        level = question_data.get("Level", "unknown")
        ground_truth = question_data.get("Final answer", "N/A")
        
        print(f"\n[{i}/{num_questions}] Task ID: {task_id} | Level: {level}")
        print(f"Question: {question[:100]}...")
        
        start_time = datetime.now()
        
        try:
            result = await run_workflow(
                question=question,
                task_id=task_id,
                use_structured_output=True,
                verbose=verbose
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            total_time += duration
            
            answer = result.get("answer", "Error")
            
            # Check if correct
            is_correct = str(answer).strip().lower() == str(ground_truth).strip().lower()
            if is_correct:
                correct_count += 1
                status = "✅ CORRECT"
            else:
                status = "❌ INCORRECT"
            
            print(f"Answer: {answer}")
            if ground_truth != "N/A":
                print(f"Expected: {ground_truth}")
            print(f"{status} | Time: {duration:.2f}s")
            
            # Create result object
            result_obj = GAIAResult(
                task_id=task_id,
                question=question,
                submitted_answer=answer,
                ground_truth=ground_truth if ground_truth != "N/A" else None,
                correct=is_correct,
                level=level,
                execution_time=duration,
                tools_used=result.get("tools_used", [])
            )
            
            results.append(result_obj.model_dump())
        
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append({
                "task_id": task_id,
                "question": question,
                "submitted_answer": f"Error: {e}",
                "ground_truth": ground_truth if ground_truth != "N/A" else None,
                "correct": False,
                "level": level,
                "execution_time": 0,
            })
    
    # Summary
    print("\n" + "="*80)
    print("BATCH TEST SUMMARY")
    print("="*80)
    print(f"\nTotal Questions: {num_questions}")
    print(f"Correct Answers: {correct_count}")
    print(f"Accuracy: {(correct_count/num_questions)*100:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time per Question: {total_time/num_questions:.2f}s")
    
    # Calculate by level
    level_stats = {}
    for result in results:
        level = result['level']
        if level not in level_stats:
            level_stats[level] = {'total': 0, 'correct': 0}
        level_stats[level]['total'] += 1
        if result['correct']:
            level_stats[level]['correct'] += 1
    
    print("\nAccuracy by Level:")
    for level in sorted(level_stats.keys()):
        stats = level_stats[level]
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  Level {level}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_v2_{timestamp}.json"
    
    summary = {
        "timestamp": timestamp,
        "model": settings.agent.model_name,
        "use_structured_output": True,
        "total": num_questions,
        "correct": correct_count,
        "accuracy": (correct_count/num_questions)*100,
        "total_time": total_time,
        "avg_time": total_time/num_questions,
        "level_stats": level_stats,
        "results": results
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Results saved to: {results_file}")
    print("\n" + "="*80 + "\n")
    
    return summary


def main():
    """Main entry point for testing."""
    print("\n" + "="*80)
    print("ENHANCED GAIA AGENT TESTING SUITE")
    print("="*80)
    
    # Validate configuration
    print("\nValidating configuration...")
    from config.settings import validate_settings
    issues = validate_settings()
    
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
        
        # Check if critical issues exist
        critical = any("HF_TOKEN" in issue for issue in issues)
        if critical:
            print("\n❌ Critical configuration missing. Please fix and retry.")
            return
        else:
            print("\n⚠️  Some optional features may not be available.")
    else:
        print("✅ Configuration valid")
    
    # Show settings
    print("\nCurrent Settings:")
    print(f"  Model: {settings.agent.model_name}")
    print(f"  Temperature: {settings.agent.temperature}")
    print(f"  Max Iterations: {settings.agent.max_iterations}")
    print(f"  Structured Output: {settings.agent.use_structured_output}")
    
    # Configuration
    print("\nTest Mode:")
    print("  1. Single Question Test (default)")
    print("  2. Batch Test (5 questions)")
    print("  3. Batch Test (10 questions)")
    print("  4. Batch Test (custom number)")
    
    choice = input("\nSelect mode (1-4) [1]: ").strip() or "1"
    
    # Run tests
    if choice == "1":
        asyncio.run(test_single_question(verbose=True))
    elif choice == "2":
        asyncio.run(test_batch_questions(num_questions=5, verbose=False))
    elif choice == "3":
        asyncio.run(test_batch_questions(num_questions=10, verbose=False))
    elif choice == "4":
        num = int(input("Enter number of questions: ").strip())
        asyncio.run(test_batch_questions(num_questions=num, verbose=False))
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()

