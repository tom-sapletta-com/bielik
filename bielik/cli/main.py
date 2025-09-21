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
from ..config import get_config, get_logger
from ..content_processor import get_content_processor
from ..hf_models import get_model_manager


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Bielik - Polish AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  bielik                                    # Standard session
  bielik --model other-model               # Use different model
  bielik --setup                           # Run interactive configuration
  bielik --no-setup                        # Skip automatic configuration
  bielik --use-local                       # Use local HF models
  bielik --local-model MODEL_NAME          # Specify local model
        """
    )
    
    config = get_config()
    
    parser.add_argument(
        "--model", 
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
        "--host",
        default=config.OLLAMA_HOST,
        help=f"Ollama server address (default: {config.OLLAMA_HOST})"
    )
    
    parser.add_argument(
        "--use-local",
        action="store_true",
        help="Use local HF models instead of Ollama"
    )
    
    parser.add_argument(
        "--local-model",
        help="Name of local HF model to use"
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
    
    # Handle CLI arguments
    current_model = args.model
    use_local_model = args.use_local
    if args.local_model:
        current_model = args.local_model
        use_local_model = True
    
    # Update configuration if host is specified
    if args.host != config.OLLAMA_HOST:
        # Note: In a full implementation, we might want to update the config object
        logger.info(f"Using custom Ollama host: {args.host}")
    
    # Show welcome message
    command_processor.show_welcome()
    
    # Force setup if requested
    if args.setup:
        print("🔧 Running interactive configuration...")
        print()
        if not setup_manager.interactive_setup():
            print("❌ Configuration failed.")
            return
        print()
    
    # Check system status and offer setup if needed
    if not args.no_setup:
        status = setup_manager.check_system_status(current_model)
        print(f"🔗 Status: {status}")
        
        if "❌" in status:
            print()
            
            try:
                setup_choice = input("🤔 Would you like to run automatic configuration? (Y/n): ").strip().lower()
                if setup_choice not in ['n', 'no']:
                    print()
                    if setup_manager.interactive_setup():
                        # Recheck status after setup
                        status = setup_manager.check_system_status(current_model)
                        print(f"🔗 New status: {status}")
                        print()
                    else:
                        print("❌ Automatic configuration failed.")
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Configuration interrupted by user")
                return

    # If still having issues, offer to continue anyway
    if "❌" in setup_manager.check_system_status(current_model):
        print("📖 Manual repair instructions:")
        print("  1. Install Ollama: https://ollama.com")
        print("  2. Run: ollama serve")
        print(f"  3. Install model: ollama pull {current_model}")
        print("  4. Check: ollama list")
        print()

        try:
            continue_anyway = input("Continue despite problems? (y/N): ")
            if continue_anyway.lower() not in ['y', 'yes']:
                print("Session ended. Fix configuration and try again.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            return
        print()

    print("🚀 Ready to chat! Write something...")
    print("─" * 53)

    # Initialize conversation
    system_prompt = ("You are Bielik, a helpful Polish AI assistant. "
                     "Respond in Polish unless asked otherwise.")
    messages = [{"role": "system", "content": system_prompt}]

    # Main chat loop
    try:
        while True:
            try:
                user_input = input("\n🧑 You: ").strip()
            except EOFError:
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            # Handle special commands
            if command_processor.is_command(user_input):
                continue_chat, new_model, updated_messages = command_processor.process_command(
                    user_input, messages, current_model
                )
                
                if not continue_chat:
                    break
                
                if new_model is not None:
                    current_model = new_model
                    # If switching to local model, enable local mode
                    if current_model in hf_model_manager.SPEAKLEASH_MODELS:
                        use_local_model = True
                    else:
                        use_local_model = args.use_local or (args.local_model is not None)
                
                messages = updated_messages
                continue

            # Process content in user message (URLs, file paths)
            enhanced_user_content = content_processor.process_content_in_text(user_input)
            
            messages.append({"role": "user", "content": enhanced_user_content})
            print("🦅 Bielik thinking...", end="", flush=True)

            # Send message to model
            response = send_chat(messages, model=current_model, use_local=use_local_model)
            print("\r🦅 Bielik: " + " "*20)  # Clear "thinking" message
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
