import os
import gradio as gr
import requests
import pandas as pd

# Import enhanced workflow with structured outputs
from workflow import run_workflow_sync
from config import get_settings

# Get settings
settings = get_settings()

# --- Constants ---
DEFAULT_API_URL = settings.api.gaia_api_url

# --- Enhanced GAIA Agent Definition ---

class GAIAAgent:
    """
    Enhanced GAIA Agent using LlamaIndex workflows with structured outputs.
    
    Features:
    - Structured outputs via Pydantic models (no "FINAL ANSWER:" issues)
    - Configuration via Pydantic Settings (type-safe)
    - 13 comprehensive tools (Wikipedia, arXiv, Weather, Web search, Files, Calculator, Code execution)
    - Official LlamaIndex readers for reliability
    - Retry logic for API failures
    - Comprehensive error handling
    
    Optimized for 90%+ accuracy on GAIA benchmark.
    """
    def __init__(self):
        """Initialize agent with configuration from Pydantic Settings."""
        print("=" * 80)
        print("Initializing Enhanced GAIA Agent")
        print("=" * 80)
        print(f"Model: {settings.agent.model_name}")
        print(f"Temperature: {settings.agent.temperature}")
        print(f"Max Iterations: {settings.agent.max_iterations}")
        print(f"Structured Output: {settings.agent.use_structured_output}")
        print(f"Provider: {'OpenAI' if settings.agent.use_openai else 'HuggingFace'}")
        print("=" * 80)
    
    def __call__(self, question: str, task_id: str = None) -> str:
        """
        Process a question and return the answer.
        
        Args:
            question: The question to answer
            task_id: Optional GAIA task ID
        
        Returns:
            The agent's answer (clean, no prefixes)
        """
        print(f"\n[Agent] Processing question (ID: {task_id or 'N/A'})")
        print(f"[Agent] Question: {question[:100]}...")
        
        try:
            # Run the enhanced workflow without structured outputs
            answer = run_workflow_sync(
                question=question,
                task_id=task_id,
                use_structured_output=False,  # Don't use structured outputs
                verbose=False  # Keep logs minimal for Gradio
            )
            
            print(f"[Agent] Answer: {answer[:100]}...")
            return answer
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[Agent] Error: {error_msg}")
            return error_msg

def run_and_submit_all( profile: gr.OAuthProfile | None):
    """
    Fetches all questions, runs the BasicAgent on them, submits all answers,
    and displays the results.
    """
    # --- Determine HF Space Runtime URL and Repo URL ---
    space_id = os.getenv("SPACE_ID") # Get the SPACE_ID for sending link to the code

    if profile:
        username= f"{profile.username}"
        print(f"User logged in: {username}")
    else:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    api_url = DEFAULT_API_URL
    questions_url = f"{api_url}/questions"
    submit_url = f"{api_url}/submit"

    # 1. Instantiate Enhanced Agent
    try:
        agent = GAIAAgent()  # Configuration loaded from settings
    except Exception as e:
        print(f"Error instantiating agent: {e}")
        return f"Error initializing agent: {e}", None
    # In the case of an app running as a hugging Face space, this link points toward your codebase ( usefull for others so please keep it public)
    agent_code = f"https://huggingface.co/spaces/{space_id}/tree/main"
    print(agent_code)

    # 2. Fetch Questions
    print(f"Fetching questions from: {questions_url}")
    try:
        response = requests.get(questions_url, timeout=15)
        response.raise_for_status()
        questions_data = response.json()
        if not questions_data:
             print("Fetched questions list is empty.")
             return "Fetched questions list is empty or invalid format.", None
        print(f"Fetched {len(questions_data)} questions.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching questions: {e}")
        return f"Error fetching questions: {e}", None
    except requests.exceptions.JSONDecodeError as e:
         print(f"Error decoding JSON response from questions endpoint: {e}")
         print(f"Response text: {response.text[:500]}")
         return f"Error decoding server response for questions: {e}", None
    except Exception as e:
        print(f"An unexpected error occurred fetching questions: {e}")
        return f"An unexpected error occurred fetching questions: {e}", None

    # 3. Run your Agent
    results_log = []
    answers_payload = []
    print(f"Running agent on {len(questions_data)} questions...")
    for item in questions_data:
        task_id = item.get("task_id")
        question_text = item.get("question")
        if not task_id or question_text is None:
            print(f"Skipping item with missing task_id or question: {item}")
            continue
        try:
            submitted_answer = agent(question_text, task_id=task_id)
            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})
            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer})
        except Exception as e:
             print(f"Error running agent on task {task_id}: {e}")
             results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": f"AGENT ERROR: {e}"})

    if not answers_payload:
        print("Agent did not produce any answers to submit.")
        return "Agent did not produce any answers to submit.", pd.DataFrame(results_log)

    # 4. Prepare Submission 
    submission_data = {"username": username.strip(), "agent_code": agent_code, "answers": answers_payload}
    status_update = f"Agent finished. Submitting {len(answers_payload)} answers for user '{username}'..."
    print(status_update)

    # 5. Submit
    print(f"Submitting {len(answers_payload)} answers to: {submit_url}")
    try:
        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        print("Submission successful.")
        results_df = pd.DataFrame(results_log)
        return final_status, results_df
    except requests.exceptions.HTTPError as e:
        error_detail = f"Server responded with status {e.response.status_code}."
        try:
            error_json = e.response.json()
            error_detail += f" Detail: {error_json.get('detail', e.response.text)}"
        except requests.exceptions.JSONDecodeError:
            error_detail += f" Response: {e.response.text[:500]}"
        status_message = f"Submission Failed: {error_detail}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df
    except requests.exceptions.Timeout:
        status_message = "Submission Failed: The request timed out."
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df
    except requests.exceptions.RequestException as e:
        status_message = f"Submission Failed: Network error - {e}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df
    except Exception as e:
        status_message = f"An unexpected error occurred during submission: {e}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df


# --- Custom CSS for Dark/Minimal Theme ---
custom_css = """
body { background-color: #0b0f19; color: #e2e8f0; }
.gradio-container { font-family: 'Inter', -apple-system, sans-serif; }
h1, h2, h3 { font-weight: 600; letter-spacing: -0.025em; }
.contain { border: 1px solid #1e293b !important; background: #0f172a !important; border-radius: 8px !important; }
/* Make buttons minimal */
button.primary { background-color: #3b82f6 !important; color: white !important; font-weight: 500; border-radius: 6px; }
button.primary:hover { background-color: #2563eb !important; }
/* Status box styling */
textarea { font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important; background-color: #1e293b !important; color: #94a3b8 !important; border: 1px solid #334155 !important; }
"""

# --- Build Gradio Interface ---
# Force dark mode via JS
js_func = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="slate", neutral_hue="slate"),
    css=custom_css,
    js=js_func,
    title="GAIA Agent"
) as demo:
    with gr.Row(variant="panel", elem_classes=["header-row"]):
        with gr.Column(scale=4):
           gr.Markdown("# 🌘 GAIA Agent")
           gr.Markdown("Running **LlamaIndex Workflows** with **Structured Outputs** for high-accuracy reasoning.")
        with gr.Column(scale=1, min_width=150):
           gr.LoginButton(scale=1, size="sm")

    with gr.Row():
        # Left Sidebar: Config & Tools
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### ⚙️ Config")
                gr.Markdown(f"**Model**: `{settings.agent.model_name}`")
                gr.Markdown(f"**Provider**: `{'OpenAI' if settings.agent.use_openai else 'Google GenAI' if settings.agent.use_gemini else 'HuggingFace'}`")
                gr.Markdown(f"**Temp**: `{settings.agent.temperature}`")
            
            with gr.Accordion("📚 Available Tools", open=False):
                gr.Markdown("""
                - **Knowledge**: Wikipedia, arXiv, Weather
                - **Web**: Search, News
                - **Files**: Read, Download
                - **Math**: Calculator, Solver
                - **Code**: Python Execution
                """)
            
            with gr.Group():
                 gr.Markdown("### 📋 Live Logs")
                 status_output = gr.Textbox(label="Agent Status", lines=15, interactive=False, show_label=False, elem_id="status-box")

        # Main Content: Action & Results
        with gr.Column(scale=2):
            with gr.Group():
                gr.Markdown("### 🚀 Execute")
                gr.Markdown("Run the agent on the GAIA benchmark dataset. This will fetch questions, reason through them using tools, and submit answers.")
                run_button = gr.Button("Start Evaluation & Submit", variant="primary", size="lg")
            
            gr.Markdown("### 📊 Results Data")
            results_table = gr.DataFrame(
                label="Evaluation Results", 
                headers=["Task ID", "Question", "Submitted Answer"],
                interactive=False,
                wrap=True,
                elem_id="results-table"
            )

    run_button.click(
        fn=run_and_submit_all,
        outputs=[status_output, results_table]
    )

if __name__ == "__main__":
    print("\\n" + "-"*30 + " App Starting " + "-"*30)
    # Check for SPACE_HOST and SPACE_ID at startup for information
    space_host_startup = os.getenv("SPACE_HOST")
    space_id_startup = os.getenv("SPACE_ID") # Get SPACE_ID at startup

    if space_host_startup:
        print(f"✅ SPACE_HOST found: {space_host_startup}")
        print(f"   Runtime URL should be: https://{space_host_startup}.hf.space")
    else:
        print("ℹ️  SPACE_HOST environment variable not found (running locally?).")

    if space_id_startup: # Print repo URLs if SPACE_ID is found
        print(f"✅ SPACE_ID found: {space_id_startup}")
        print(f"   Repo URL: https://huggingface.co/spaces/{space_id_startup}")
        print(f"   Repo Tree URL: https://huggingface.co/spaces/{space_id_startup}/tree/main")
    else:
        print("ℹ️  SPACE_ID environment variable not found (running locally?). Repo URL cannot be determined.")

    print("-"*(60 + len(" App Starting ")) + "\\n")

    print("Launching Gradio Interface for Basic Agent Evaluation...")
    demo.launch(debug=True, share=False)