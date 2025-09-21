#!/usr/bin/env python3
"""
Bielik CLI Main - Main chat loop and argument parsing.

This module provides the main entry point for the Bielik CLI application,
including argument parsing and the interactive chat loop.
"""

import sys
import argparse
from typing import List, Dict

from .commands import CommandProcessor
from .send_chat import send_chat
from .setup import SetupManager
from .settings import get_cli_settings
from ..config import get_config, get_logger
from ..content_processor import get_content_processor
from ..hf_models import get_model_manager


def validate_model_availability(model_name: str, model_manager) -> bool:
    """Check if a HuggingFace model is available locally."""
    try:
        # Check if it's a HuggingFace model and is downloaded
        if model_name in model_manager.SPEAKLEASH_MODELS:
            return model_manager.is_model_downloaded(model_name)
        
        return False
    except Exception:
        return False


def find_fallback_model(model_manager):
    """Find a working fallback HuggingFace model."""
    # Try to find downloaded HF models from registry
    try:
        registry = model_manager.list_downloaded_models()
        if registry:
            # Get the first available HF model from registry
            for model_name, model_info in registry.items():
                if model_manager.is_model_downloaded(model_name):
                    print(f"🔍 Found downloaded HF model: {model_name}")
                    return model_name
    except Exception as e:
        print(f"⚠️  Could not check HF models registry: {e}")
    
    return None


def execute_prompt(prompt: str, model: str, use_local: bool = True) -> str:
    """Execute a single prompt - handles both Context Provider Commands and AI model queries."""
    from .send_chat import send_chat
    from ..content_processor import get_content_processor
    from ..hf_models import HAS_LLAMA_CPP
    from .command_api import get_command_registry
    
    # Initialize components
    content_processor = get_content_processor()
    cli_settings = get_cli_settings()
    hf_model_manager = get_model_manager()
    command_registry = get_command_registry()
    
    # Check if this is a CLI command (format: ":commandname args") or Context Provider Command (format: "commandname: args")
    if ':' in prompt and not prompt.startswith('http'):
        # Check for regular CLI command first (format: ":command args")
        if prompt.startswith(':'):
            parts = prompt[1:].split(' ', 1)  # Remove ':' and split on first space
            potential_command = parts[0].strip()
            command_args = parts[1].strip() if len(parts) > 1 else ""
            
            # Check if this command exists in the registry
            available_commands = command_registry.list_commands()
            if potential_command in available_commands:
                command = command_registry.get_command(potential_command)
                if command and not getattr(command, 'is_context_provider', False):
                    # This is a regular CLI command - execute it independently of AI models
                    try:
                        context = {
                            'current_model': model,
                            'messages': [],
                            'cli_settings': cli_settings
                        }
                        # Parse command arguments
                        args = [f":{potential_command}"] + command_args.split() if command_args else [f":{potential_command}"]
                        result = command_registry.execute_command(potential_command, args, context)
                        return result
                    except Exception as e:
                        return f"❌ Error executing :{potential_command} command: {e}"
        
        # Check for Context Provider Command (format: "commandname: args")
        else:
            parts = prompt.split(':', 1)
            if len(parts) == 2:
                potential_command = parts[0].strip()
                command_args = parts[1].strip()
                
                # Check if this command exists in the registry
                available_commands = command_registry.list_commands()
                if potential_command in available_commands:
                    command = command_registry.get_command(potential_command)
                    if command and getattr(command, 'is_context_provider', False):
                        # This is a Context Provider Command - execute it independently of AI models
                        try:
                            context = {
                                'current_model': model,
                                'messages': [],
                                'cli_settings': cli_settings
                            }
                            # Parse command arguments
                            args = [f"{potential_command}:"] + command_args.split() if command_args else [f"{potential_command}:"]
                            result = command_registry.execute_command(potential_command, args, context)
                            return result
                        except Exception as e:
                            return f"❌ Error executing {potential_command}: command: {e}"
    
    # Process content in user message (URLs, file paths)
    enhanced_prompt = content_processor.process_content_in_text(prompt)
    
    # For AI model queries, check if llama-cpp-python is available
    if not HAS_LLAMA_CPP:
        return "[LOCAL MODEL ERROR] llama-cpp-python not installed. Install with: pip install 'bielik[local]'"
    
    # Check if model is downloaded
    if not hf_model_manager.is_model_downloaded(model):
        return f"[LOCAL MODEL ERROR] Model {model} not downloaded. Use :download {model}"
    
    # Prepare system prompt with dynamic assistant name for AI model
    assistant_name = cli_settings.get_assistant_name()
    system_prompt = (f"You are {assistant_name}, a helpful Polish AI assistant. "
                     f"Respond in Polish unless asked otherwise.")
    
    # Create messages for AI model
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": enhanced_prompt}
    ]
    
    # Send to local HF model
    return send_chat(messages, model=model, use_local=True)


def run_model_tests(model: str, use_local: bool = False) -> None:
    """Run a series of tests on the specified model."""
    print(f"🧪 Running model tests for: {model}")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Basic Math",
            "prompt": "Ile jest 2 + 2?",
            "expected_keywords": ["4", "cztery"]
        },
        {
            "name": "Polish Language",
            "prompt": "Napisz krótkie zdanie po polsku o pogodzie",
            "expected_keywords": ["pogoda", "słońce", "deszcz", "chmury", "temperatura"]
        },
        {
            "name": "Simple Question",
            "prompt": "Co to jest sztuczna inteligencja?",
            "expected_keywords": ["AI", "inteligencja", "komputer", "algorytm", "uczenie"]
        },
        {
            "name": "Creative Writing",
            "prompt": "Napisz krótką historyjkę o kocie",
            "expected_keywords": ["kot", "miau", "łapy", "ogon"]
        },
        {
            "name": "Code Generation",
            "prompt": "Napisz prostą funkcję Python, która dodaje dwie liczby",
            "expected_keywords": ["def", "return", "+", "python"]
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print("\n🧪 Test " + str(i) + "/5: " + test['name'])
        print("📝 Prompt: " + test['prompt'])
        
        try:
            response = execute_prompt(test['prompt'], model, use_local)
            print(f"🤖 Response: {response[:100]}...")
            
            # Check if response contains expected keywords
            response_lower = response.lower()
            found_keywords = [kw for kw in test['expected_keywords'] 
                            if kw.lower() in response_lower]
            
            success = len(found_keywords) > 0
            results.append({
                'test': test['name'],
                'success': success,
                'keywords_found': found_keywords,
                'response_length': len(response)
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"📊 Status: {status} (Found: {', '.join(found_keywords)})")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                'test': test['name'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print("✅ Passed: " + str(passed) + "/" + str(total))
    print("❌ Failed: " + str(total - passed) + "/" + str(total))
    print("📈 Success Rate: " + str(round((passed/total)*100, 1)) + "%")
    
    if passed == total:
        print("\n🎉 All tests passed! Model " + model + " is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check model configuration or connectivity.")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Bielik - Polish AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  bielik                                         # Standard interactive session with local HF models
  bielik --model bielik-7b-instruct             # Use specific HF model
  bielik --setup                                # Run interactive configuration
  bielik --no-setup                             # Skip automatic configuration
  bielik --local-model bielik-4.5b-v3.0        # Specify local HF model
  bielik -p "napisz ile jest dwa razy dwa"     # Execute single prompt
  bielik --prompt "What is 2+2?"               # Execute single prompt (alias)
  bielik -p "test" -m bielik-4.5b-v3.0         # Execute prompt with specific HF model
  bielik --prompt "test" --model bielik-7b     # Execute prompt with HF model (long form)
  bielik --test-model                           # Run model performance tests
  bielik --test-model -m bielik-4.5b-v3.0      # Test specific HF model

Powered by HuggingFace + SpeakLeash - Local AI models for everyone!
        """
    )
    
    config = get_config()
    
    parser.add_argument(
        "-m", "--model", 
        default=config.BIELIK_MODEL,
        help=f"Model to use (default: {config.BIELIK_MODEL})"
    )
    
    parser.add_argument(
        "--setup", 
        action="store_true",
        help="Run interactive system configuration"
    )
    
    parser.add_argument(
        "--no-setup", 
        action="store_true",
        help="Skip automatic configuration when problems occur"
    )
    
    
    parser.add_argument(
        "--use-local",
        action="store_true",
        help="Force use local HF models (default behavior)"
    )
    
    parser.add_argument(
        "--local-model",
        help="Name of local HF model to use"
    )
    
    parser.add_argument(
        "-p", "--prompt",
        help="Execute single prompt and exit (non-interactive mode)"
    )
    
    parser.add_argument(
        "--test-model",
        action="store_true",
        help="Run model tests and exit"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for Bielik CLI."""
    args = parse_args()
    
    # Initialize components
    config = get_config()
    logger = get_logger(__name__)
    content_processor = get_content_processor()
    command_processor = CommandProcessor()
    setup_manager = SetupManager()
    hf_model_manager = get_model_manager()
    cli_settings = get_cli_settings()
    
    # Smart model selection with .env fallback
    current_model = args.model
    use_local_model = args.use_local
    
    # Load last used model from .env if no model specified via CLI
    if current_model == config.BIELIK_MODEL:  # Default model from config
        env_model = cli_settings.get_current_model()
        if env_model and env_model != config.BIELIK_MODEL:
            current_model = env_model
            logger.info(f"Loaded last used model from .env: {current_model}")
    
    # Handle local model specification
    if args.local_model:
        current_model = args.local_model
        use_local_model = True
    
    # Validate model availability and set fallback logic
    model_available = validate_model_availability(current_model, hf_model_manager)
    if not model_available:
        # Try to find a working fallback model
        fallback_model = find_fallback_model(hf_model_manager)
        if fallback_model:
            print(f"⚠️  Model '{current_model}' not available, using fallback: {fallback_model}")
            current_model = fallback_model
            if current_model in hf_model_manager.SPEAKLEASH_MODELS:
                use_local_model = True
        else:
            print(f"❌ No working models available. Please check your configuration.")
            if not args.prompt and not args.test_model:
                print("💡 Try: bielik --setup")
                sys.exit(1)
    
    # Handle non-interactive modes
    if args.prompt:
        # Execute single prompt and exit
        try:
            print(f"🤖 Using model: {current_model}")
            response = execute_prompt(args.prompt, current_model, use_local_model)
            print(response)
            return
        except Exception as e:
            print(f"❌ Error executing prompt: {str(e)}")
            sys.exit(1)
    
    if args.test_model:
        # Run model tests and exit
        try:
            run_model_tests(current_model, use_local_model)
            return
        except Exception as e:
            print(f"❌ Error running tests: {str(e)}")
            sys.exit(1)
    
    
    # Show welcome message
    command_processor.show_welcome()
    
    # Force setup if requested (for HF model downloads)
    if args.setup:
        print("🔧 Running HF model configuration...")
        print("💡 Use ':download <model>' to download HuggingFace models")
        print("💡 Available models: bielik-7b-instruct, bielik-4.5b-v3.0-instruct")
        print()
    
    # Check local HF model availability
    if not args.no_setup:
        # Simple check for llama-cpp-python and downloaded models
        from ..hf_models import HAS_LLAMA_CPP
        
        if not HAS_LLAMA_CPP:
            print("❌ llama-cpp-python not installed")
            print("💡 Install with: pip install 'bielik[local]'")
            print()
        elif not hf_model_manager.is_model_downloaded(current_model):
            print(f"❌ Model '{current_model}' not downloaded locally")
            print(f"💡 Download with: :download {current_model}")
            print()
        else:
            print("✅ Local HF model ready")
            print()

    print("🚀 Ready to chat! Write something...")
    print("─" * 53)

    # Initialize conversation with dynamic assistant name
    assistant_name = cli_settings.get_assistant_name()
    system_prompt = (f"You are {assistant_name}, a helpful Polish AI assistant. "
                     f"Respond in Polish unless asked otherwise.")
    messages = [{"role": "system", "content": system_prompt}]
    
    # Initialize context storage for Context Provider commands
    current_context = None
    
    # Update current model setting if specified via CLI
    if current_model:
        cli_settings.set_current_model(current_model)

    # Main chat loop
    try:
        while True:
            try:
                user_prompt = cli_settings.get_user_prompt_prefix()
                user_input = input("\n" + user_prompt + " ").strip()
            except EOFError:
                print("\n👋 Goodbye " + cli_settings.get_user_name() + "!")
                break

            if not user_input:
                continue

            # Handle special commands
            if command_processor.is_command(user_input):
                continue_chat, result_data, updated_messages = command_processor.process_command(
                    user_input, messages, current_model
                )
                
                if not continue_chat:
                    break
                
                # Check if this is a Context Provider command (result_data is context string)
                if isinstance(result_data, str) and result_data.strip():
                    # Store context from Context Provider command (replaces previous context)
                    current_context = result_data
                    print("✅ Context loaded! You can now ask questions about the provided data.")
                    print("💡 Tip: Use another Context Provider command to load new context, or continue chatting.")
                    messages = updated_messages
                    continue
                
                # Handle model switching for direct commands (result_data is new_model)
                if result_data is not None and not isinstance(result_data, str):
                    current_model = result_data
                    # If switching to local model, enable local mode
                    if current_model in hf_model_manager.SPEAKLEASH_MODELS:
                        use_local_model = True
                    else:
                        use_local_model = args.use_local or (args.local_model is not None)
                
                messages = updated_messages
                continue

            # Process content in user message (URLs, file paths)
            enhanced_user_content = content_processor.process_content_in_text(user_input)
            
            # If we have context from Context Provider command, include it in the user message
            if current_context:
                enhanced_user_content = f"{current_context}\n\n---\n\nUser question: {enhanced_user_content}"
            
            messages.append({"role": "user", "content": enhanced_user_content})
            assistant_prompt = cli_settings.get_assistant_prompt_prefix()
            print(f"{assistant_prompt} thinking...", end="", flush=True)

            # Send message to model
            response = send_chat(messages, model=current_model, use_local=use_local_model)
            print(f"\r{assistant_prompt} " + " "*20)  # Clear "thinking" message
            print(f"    {response}")

            # Only add to history if it's a real response, not an error
            error_prefixes = ["[ERROR]", "[REST ERROR]", "[OLLAMA LIB ERROR]", "[LOCAL MODEL ERROR]"]
            if not any(response.startswith(prefix) for prefix in error_prefixes):
                messages.append({"role": "assistant", "content": response})

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
