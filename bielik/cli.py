#!/usr/bin/env python3
"""
bielik CLI - interactive chat shell using Ollama.
Tries REST API first, falls back to `ollama` library if available.
"""

import os
import sys
import requests
import subprocess
import platform
import shutil
import argparse

from .config import get_config, get_logger
from .content_processor import get_content_processor
from .hf_models import get_model_manager, HAS_LLAMA_CPP

# Global configuration and logger
config = get_config()
logger = get_logger(__name__)
content_processor = get_content_processor()
model_manager = get_model_manager()

# try to import official ollama client
try:
    import ollama
    HAVE_OLLAMA = True
except ImportError:
    HAVE_OLLAMA = False


def send_chat(messages, model=None):
    """Send chat messages to Ollama via REST API or ollama lib fallback."""
    if model is None:
        model = config.BIELIK_MODEL
    
    payload = {"model": model, "messages": messages, "stream": False}

    # try REST first
    try:
        resp = requests.post(config.CHAT_ENDPOINT, json=payload, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {}).get("content")
        if msg:
            logger.debug(f"REST API successful for model {model}")
            return msg
    except Exception as e:
        logger.warning(f"REST API failed: {e}")

    # fallback: official ollama library
    if HAVE_OLLAMA:
        try:
            response = ollama.chat(model=model, messages=messages)
            logger.debug(f"Ollama library successful for model {model}")
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama library failed: {e}")
            return f"[OLLAMA LIB ERROR] {e}"

    logger.error("No working Ollama integration available")
    return "[ERROR] No working Ollama integration (REST and lib failed)."


def show_welcome():
    """Display welcome message and help for beginners."""
    print("🦅 " + "="*50)
    print("   BIELIK - Polski Asystent AI")
    print("   Powered by Ollama + Speakleash")
    print("="*53)
    print()
    print("📋 Dostępne komendy:")
    print("  :help    - pokaż tę pomoc")
    print("  :status  - sprawdź połączenie z Ollama")
    print("  :setup   - uruchom interaktywną konfigurację")
    print("  :clear   - wyczyść historię rozmowy")
    print("  :exit    - zakończ sesję")
    print("  Ctrl+C   - szybkie wyjście")
    print()
    print("💡 Wskazówki:")
    print("  • Pisz po polsku - Bielik rozumie język polski!")
    print("  • Zadawaj pytania, proś o pomoc, rozmawiaj naturalnie")
    print("  • Jeśli Ollama nie działa, zobaczysz komunikat o błędzie")
    print()


def is_ollama_installed():
    """Check if Ollama binary is installed on the system."""
    return shutil.which("ollama") is not None


def is_ollama_running():
    """Check if Ollama server is running."""
    try:
        resp = requests.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def get_installed_models():
    """Get list of installed Ollama models."""
    try:
        resp = requests.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return [m['name'] for m in data.get('models', [])]
    except Exception:
        pass
    return []


def is_bielik_model_available():
    """Check if Bielik model is available."""
    models = get_installed_models()
    return any('bielik' in model.lower() for model in models)


def install_ollama():
    """Install Ollama based on the operating system."""
    system = platform.system().lower()
    
    print("🔧 Instalowanie Ollama...")
    
    try:
        if system == "linux":
            print("📦 Wykryto Linux - używam curl do pobrania Ollama...")
            cmd = ["curl", "-fsSL", "https://ollama.com/install.sh"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                # Run the install script
                install_cmd = ["sh", "-c", result.stdout]
                subprocess.run(install_cmd, check=True, timeout=300)
                print("✅ Ollama zainstalowana pomyślnie!")
                return True
            else:
                print(f"❌ Błąd pobierania skryptu instalacji: {result.stderr}")
                return False
                
        elif system == "darwin":  # macOS
            print("📦 Wykryto macOS - sprawdzam Homebrew...")
            if shutil.which("brew"):
                subprocess.run(["brew", "install", "ollama"], check=True, timeout=300)
                print("✅ Ollama zainstalowana przez Homebrew!")
                return True
            else:
                print("❌ Homebrew nie znaleziony. Zainstaluj ręcznie z https://ollama.com")
                return False
                
        elif system == "windows":
            print("📦 Wykryto Windows - wymagana instalacja ręczna")
            print("📖 Pobierz Ollama z: https://ollama.com/download/windows")
            print("   Uruchom pobrany plik .exe i postępuj zgodnie z instrukcjami")
            return False
            
        else:
            print(f"❌ Nieobsługiwany system operacyjny: {system}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Instalacja przekroczyła limit czasu")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas instalacji: {e}")
        return False
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}")
        return False


def start_ollama_server():
    """Start Ollama server in background."""
    try:
        print("🚀 Uruchamianie serwera Ollama...")
        if platform.system().lower() == "windows":
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a bit for server to start
        import time
        time.sleep(3)
        
        if is_ollama_running():
            print("✅ Serwer Ollama uruchomiony!")
            return True
        else:
            print("⚠️ Serwer może potrzebować więcej czasu na uruchomienie...")
            return False
    except Exception as e:
        print(f"❌ Błąd uruchamiania serwera: {e}")
        return False


def pull_bielik_model():
    """Download and install Bielik model."""
    try:
        print(f"📥 Pobieranie modelu {DEFAULT_MODEL}...")
        print("⏳ To może potrwać kilka minut w zależności od połączenia...")
        
        result = subprocess.run(
            ["ollama", "pull", DEFAULT_MODEL], 
            capture_output=True, 
            text=True, 
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ Model Bielik pobrany pomyślnie!")
            return True
        else:
            print(f"❌ Błąd pobierania modelu: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Pobieranie modelu przekroczyło limit czasu (30 min)")
        return False
    except Exception as e:
        print(f"❌ Błąd pobierania modelu: {e}")
        return False


def interactive_setup():
    """Interactive setup process for first-time users."""
    print("🔍 Sprawdzanie konfiguracji systemu...")
    print()
    
    setup_needed = False
    
    # Check Ollama installation
    if not is_ollama_installed():
        print("❌ Ollama nie jest zainstalowana")
        setup_needed = True
        
        try:
            install_choice = input("🤔 Czy zainstalować Ollama automatycznie? (t/N): ").strip().lower()
            if install_choice in ['t', 'tak', 'y', 'yes']:
                if install_ollama():
                    print("✅ Ollama zainstalowana!")
                else:
                    print("❌ Instalacja nie powiodła się. Zainstaluj ręcznie z https://ollama.com")
                    return False
            else:
                print("📖 Zainstaluj Ollama ręcznie z: https://ollama.com")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Konfiguracja przerwana przez użytkownika")
            return False
    else:
        print("✅ Ollama jest zainstalowana")
    
    # Check if Ollama server is running
    if not is_ollama_running():
        print("❌ Serwer Ollama nie działa")
        setup_needed = True
        
        try:
            start_choice = input("🤔 Czy uruchomić serwer Ollama? (t/N): ").strip().lower()
            if start_choice in ['t', 'tak', 'y', 'yes']:
                if not start_ollama_server():
                    print("❌ Nie udało się uruchomić serwera. Spróbuj ręcznie: ollama serve")
                    return False
            else:
                print("📖 Uruchom serwer ręcznie: ollama serve")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Konfiguracja przerwana przez użytkownika")
            return False
    else:
        print("✅ Serwer Ollama działa")
    
    # Check if Bielik model is available
    if not is_bielik_model_available():
        print(f"❌ Model {DEFAULT_MODEL} nie jest dostępny")
        installed_models = get_installed_models()
        if installed_models:
            print(f"📋 Dostępne modele: {', '.join(installed_models[:5])}")
        setup_needed = True
        
        try:
            model_choice = input(f"🤔 Czy pobrać model {DEFAULT_MODEL}? (t/N): ").strip().lower()
            if model_choice in ['t', 'tak', 'y', 'yes']:
                if not pull_bielik_model():
                    print(f"❌ Nie udało się pobrać modelu. Spróbuj ręcznie: ollama pull {DEFAULT_MODEL}")
                    return False
            else:
                print(f"📖 Pobierz model ręcznie: ollama pull {DEFAULT_MODEL}")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Konfiguracja przerwana przez użytkownika")
            return False
    else:
        print(f"✅ Model {DEFAULT_MODEL} jest dostępny")
    
    if setup_needed:
        print()
        print("🎉 Konfiguracja zakończona pomyślnie!")
        print("🚀 Bielik jest gotowy do użycia!")
    else:
        print("✅ Wszystkie komponenty są już skonfigurowane!")
    
    return True


def check_ollama_status():
    """Check if Ollama is running and accessible."""
    try:
        # Quick health check
        resp = requests.get(f"{config.OLLAMA_HOST.rstrip('/')}/api/tags", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            models = [m['name'] for m in data.get('models', [])]
            target_model = config.BIELIK_MODEL
            if any(target_model.lower() in model.lower() for model in models):
                logger.info(f"Ollama status check: Model {target_model} available")
                return f"✅ Ollama running, model {target_model} available"
            else:
                available = ', '.join(models[:3]) if models else "none"
                logger.warning(f"Ollama running but model {target_model} not found")
                return f"⚠️ Ollama running, but model '{target_model}' missing. Available: {available}"
        else:
            logger.error(f"Ollama HTTP error: {resp.status_code}")
            return f"❌ Ollama responds but HTTP error {resp.status_code}"
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        return f"❌ Ollama unavailable: {str(e)}"


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Bielik - Polski Asystent AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  bielik                                    # Standardowa sesja
  bielik --model other-model               # Użyj innego modelu
  bielik --setup                           # Uruchom interaktywną konfigurację
  bielik --no-setup                        # Pomiń automatyczną konfigurację
        """
    )
    
    parser.add_argument(
        "--model", 
        default=DEFAULT_MODEL,
        help=f"Model do użycia (domyślny: {DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "--setup", 
        action="store_true",
        help="Uruchom interaktywną konfigurację systemu"
    )
    
    parser.add_argument(
        "--no-setup", 
        action="store_true",
        help="Pomiń automatyczną konfigurację przy problemach"
    )
    
    parser.add_argument(
        "--host",
        default=OLLAMA_HOST,
        help=f"Adres serwera Ollama (domyślny: {OLLAMA_HOST})"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Override defaults with command line arguments
    global DEFAULT_MODEL, OLLAMA_HOST, CHAT_ENDPOINT
    DEFAULT_MODEL = args.model
    OLLAMA_HOST = args.host
    CHAT_ENDPOINT = OLLAMA_HOST.rstrip("/") + "/v1/chat/completions"
    
    show_welcome()
    
    # Force setup if requested
    if args.setup:
        print("🔧 Uruchamianie interaktywnej konfiguracji...")
        print()
        if not interactive_setup():
            print("❌ Konfiguracja nie powiodła się.")
            return
        print()

    # Check Ollama status at startup
    status = check_ollama_status()
    print(f"🔗 Status: {status}")
    print()

    # Handle problems with automatic setup unless disabled
    if "❌" in status and not args.no_setup:
        print("🚨 UWAGA: Wykryto problemy z konfiguracją!")
        print()
        
        try:
            setup_choice = input("🤔 Czy uruchomić automatyczną konfigurację? (T/n): ").strip().lower()
            if setup_choice not in ['n', 'nie', 'no']:
                print()
                if interactive_setup():
                    # Recheck status after setup
                    status = check_ollama_status()
                    print(f"🔗 Nowy status: {status}")
                    print()
                else:
                    print("❌ Automatyczna konfiguracja nie powiodła się.")
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Konfiguracja przerwana przez użytkownika")
            return

    # If still having issues, offer to continue anyway
    if "❌" in status:
        print("📖 Instrukcje ręcznej naprawy:")
        print("  1. Zainstaluj Ollama: https://ollama.com")
        print("  2. Uruchom: ollama serve")
        print(f"  3. Zainstaluj model: ollama pull {DEFAULT_MODEL}")
        print("  4. Sprawdź: ollama list")
        print()

        try:
            continue_anyway = input("Czy kontynuować mimo problemów? (t/N): ")
            if continue_anyway.lower() not in ['t', 'tak', 'y', 'yes']:
                print("Sesja przerwana. Napraw konfigurację i spróbuj ponownie.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nSesja przerwana.")
            return
        print()

    print("🚀 Gotowy do rozmowy! Napisz coś...")
    print("─" * 53)

    system_prompt = ("You are Bielik, a helpful Polish AI assistant. "
                     "Respond in Polish unless asked otherwise.")
    messages = [{"role": "system", "content": system_prompt}]

    try:
        while True:
            try:
                user = input("\n🧑 Ty: ").strip()
            except EOFError:
                print("\n👋 Do zobaczenia!")
                break

            if not user:
                continue

            # Handle special commands
            if user.startswith(':'):
                if user in [":exit", ":quit", ":q"]:
                    print("👋 Do zobaczenia!")
                    break
                elif user == ":help":
                    show_welcome()
                    continue
                elif user == ":status":
                    status = check_ollama_status()
                    print(f"🔗 Status: {status}")
                    continue
                elif user == ":clear":
                    messages = [{"role": "system", "content": system_prompt}]
                    print("🧹 Historia rozmowy wyczyszczona.")
                    continue
                elif user == ":setup":
                    print("🔧 Uruchamianie interaktywnej konfiguracji...")
                    interactive_setup()
                    continue
                else:
                    help_msg = (f"❓ Nieznana komenda: {user}. "
                                "Wpisz :help aby zobaczyć dostępne komendy.")
                    print(help_msg)
                    continue

            # Process content in user message (URLs, file paths)
            enhanced_user_content = content_processor.process_content_in_text(user)
            
            messages.append({"role": "user", "content": enhanced_user_content})
            print("🦅 Bielik thinking...", end="", flush=True)

            resp = send_chat(messages, model=config.BIELIK_MODEL)
            print("\r🦅 Bielik: " + " "*20)  # Clear "thinking" message
            print(f"    {resp}")

            # Only add to history if it's a real response, not an error
            error_prefixes = ["[ERROR]", "[REST ERROR]", "[OLLAMA LIB ERROR]"]
            if not any(resp.startswith(prefix) for prefix in error_prefixes):
                messages.append({"role": "assistant", "content": resp})

    except KeyboardInterrupt:
        print("\n\n👋 Przerwano przez użytkownika. Do zobaczenia!")
        sys.exit(0)


if __name__ == "__main__":
    main()
