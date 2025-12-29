"""
Setup verification script for GAIA Agent.
Checks that all dependencies and configurations are correct.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        return False, f"Python 3.9+ required, found {version.major}.{version.minor}"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        "llama_index",
        "gradio",
        "requests",
        "httpx",
        "dotenv",
        "sympy",
        "numpy",
        "pandas",
        "PIL",
    ]
    
    missing = []
    installed = []
    
    for package in required_packages:
        try:
            if package == "PIL":
                __import__("PIL")
            elif package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    return len(missing) == 0, installed, missing


def check_env_file():
    """Check if .env file exists and has required keys."""
    env_path = Path(".env")
    
    if not env_path.exists():
        return False, ".env file not found"
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    has_hf_token = "HF_TOKEN=" in content or "HUGGINGFACE_API_KEY=" in content
    
    if not has_hf_token:
        return False, ".env file missing HF_TOKEN or HUGGINGFACE_API_KEY"
    
    return True, ".env file configured"


def check_api_keys():
    """Check if API keys are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    keys = {
        "HuggingFace Token": hf_token is not None,
        "OpenAI API Key (optional)": openai_key is not None,
    }
    
    return keys


def check_files():
    """Check if all required files exist."""
    required_files = [
        "tools/registry.py",
        "agent.py",
        "workflow.py",
        "test_agent.py",
        "app.py",
        "config/settings.py",
        "requirements.txt",
    ]
    
    missing = []
    present = []
    
    for file in required_files:
        if Path(file).exists():
            present.append(file)
        else:
            missing.append(file)
    
    return len(missing) == 0, present, missing


def test_imports():
    """Test importing main modules."""
    modules_to_test = [
        ("tools.registry", "get_all_tools"),
        ("agent", "create_agent"),
        ("workflow", "run_workflow_sync"),
        ("config", "get_settings"),
    ]
    
    results = {}
    
    for module_name, attr_name in modules_to_test:
        try:
            module = __import__(module_name)
            if hasattr(module, attr_name):
                results[module_name] = True
            else:
                results[module_name] = f"Missing attribute: {attr_name}"
        except Exception as e:
            results[module_name] = f"Import error: {str(e)}"
    
    return results


def main():
    """Run all checks and display results."""
    print("="*80)
    print("GAIA AGENT SETUP VERIFICATION")
    print("="*80)
    
    # Check Python version
    print("\n📌 Python Version:")
    success, message = check_python_version()
    print(f"  {'✓' if success else '✗'} {message}")
    if not success:
        print("\n⚠️  Please upgrade to Python 3.9 or higher")
        return False
    
    # Check files
    print("\n📁 Required Files:")
    success, present, missing = check_files()
    print(f"  {'✓' if success else '✗'} {len(present)}/{len(present) + len(missing)} files present")
    if missing:
        print(f"  Missing files:")
        for file in missing:
            print(f"    - {file}")
    
    # Check dependencies
    print("\n📦 Dependencies:")
    success, installed, missing = check_dependencies()
    print(f"  {'✓' if success else '✗'} {len(installed)}/{len(installed) + len(missing)} packages installed")
    if missing:
        print(f"  Missing packages:")
        for package in missing:
            print(f"    - {package}")
        print("\n  Install with: uv sync")
    
    # Check .env file
    print("\n🔑 Environment Configuration:")
    success, message = check_env_file()
    print(f"  {'✓' if success else '✗'} {message}")
    if not success:
        print("\n  Create .env file with:")
        print("    HF_TOKEN=your_token_here")
    
    # Check API keys
    if success:
        print("\n🔐 API Keys:")
        keys = check_api_keys()
        for key_name, is_set in keys.items():
            print(f"  {'✓' if is_set else '✗'} {key_name}")
    
    # Test imports
    print("\n🧪 Module Imports:")
    results = test_imports()
    all_success = True
    for module, result in results.items():
        if result is True:
            print(f"  ✓ {module}")
        else:
            print(f"  ✗ {module}: {result}")
            all_success = False
    
    # Final verdict
    print("\n" + "="*80)
    if all_success and success:
        print("✅ SETUP COMPLETE - Ready to run!")
        print("\nNext steps:")
        print("  1. Test single question: uv run test_agent.py")
        print("  2. Run Gradio app: uv run app.py")
        print("  3. Submit to GAIA: Use the Gradio interface")
    else:
        print("⚠️  SETUP INCOMPLETE - Please fix the issues above")
        print("\nQuick fixes:")
        print("  1. Install dependencies: uv sync")
        print("  2. Create .env file with your HF_TOKEN")
        print("  3. Verify all files are present")
    print("="*80 + "\n")
    
    return all_success and success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

