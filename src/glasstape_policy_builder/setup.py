"""
Setup and installation checks for GlassTape Policy Builder.

Validates environment and dependencies before running the MCP server.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_python_version() -> bool:
    """Check Python version >= 3.10."""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_cerbos_installation() -> bool:
    """Check if Cerbos CLI is installed and accessible."""
    try:
        result = subprocess.run(
            ['cerbos', 'version'],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False  # Prevent shell injection
        )
        if result.returncode == 0:
            version_info = result.stdout.strip().split('\n')[0]
            print(f"✅ Cerbos CLI installed: {version_info}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    
    print("❌ Cerbos CLI not found")
    print("\n📦 Install Cerbos:")
    print("   macOS:  brew install cerbos/tap/cerbos")
    print("   Linux:  curl -L https://github.com/cerbos/cerbos/releases/latest/download/cerbos_Linux_x86_64 \\")
    print("             -o /usr/local/bin/cerbos && chmod +x /usr/local/bin/cerbos")
    print("   Windows: Download from https://github.com/cerbos/cerbos/releases")
    return False


def check_mcp_dependencies() -> bool:
    """Check if required MCP dependencies are available."""
    try:
        import mcp
        # Try to get version, fallback to generic message if not available
        try:
            version = getattr(mcp, '__version__', 'unknown')
            print(f"✅ MCP SDK available: {version}")
        except:
            print("✅ MCP SDK available")
        return True
    except ImportError:
        print("❌ MCP SDK not found")
        print("   Install with: pip install mcp")
        return False


def check_llm_configuration() -> bool:
    """Check LLM configuration (optional)."""
    provider = os.getenv('LLM_PROVIDER')
    
    if not provider:
        print("🎯 No LLM provider configured (client-LLM mode)")
        print("   This is the recommended configuration!")
        return True
    
    print(f"🤖 LLM_PROVIDER={provider} (server-LLM mode)")
    print("   ⚠️  Client-LLM mode is recommended for security")
    
    # Check for corresponding API key
    if provider == 'anthropic':
        if os.getenv('ANTHROPIC_API_KEY'):
            print("   ✅ ANTHROPIC_API_KEY is configured")
            return True
        else:
            print("   ❌ ANTHROPIC_API_KEY not set")
            return False
    
    elif provider in ['bedrock', 'openai']:
        print(f"   ⚠️  {provider} adapter not yet implemented")
        return False
    
    else:
        print(f"   ❌ Unknown LLM_PROVIDER: {provider}")
        return False


def check_work_directory() -> bool:
    """Check if work directory can be created."""
    work_dir = Path("/tmp/glasstape-policies")
    try:
        work_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Work directory accessible: {work_dir}")
        return True
    except PermissionError:
        print(f"❌ Cannot create work directory: {work_dir}")
        print("   Check file system permissions")
        return False


def main():
    """Run all setup checks."""
    print("🚀 GlassTape Agent Policy Builder - Setup Check")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("MCP Dependencies", check_mcp_dependencies),  
        ("Cerbos CLI", check_cerbos_installation),
        ("LLM Configuration", check_llm_configuration),
        ("Work Directory", check_work_directory),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    all_critical_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20} {status}")
        
        # Cerbos CLI and LLM config are not critical for basic operation
        if name not in ["Cerbos CLI", "LLM Configuration"] and not passed:
            all_critical_passed = False
    
    print("=" * 60)
    
    if all_critical_passed:
        print("🎉 Ready to run! Core requirements met.")
        print("\n💡 Quick start:")
        print("   glasstape-policy-builder-mcp")
        if not any(name == "Cerbos CLI" and passed for name, passed in results):
            print("\n⚠️  Install Cerbos CLI to enable policy validation and testing")
    else:
        print("⚠️  Some critical checks failed. Review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()