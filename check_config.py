"""
Check current LLM configuration
"""

import json
import os

print("=" * 60)
print("🔧 LabAcc Copilot Configuration Check")
print("=" * 60)

# Load config
with open("src/config/llm_config.json", "r") as f:
    config = json.load(f)

# Show model assignments
print("\n📋 Model Assignments:")
for role, model in config["agent_model_assignments"].items():
    print(f"  {role:20} → {model}")

# Check for react_agent specifically
react_model = config["agent_model_assignments"].get("react_agent", "Not configured")
default_model = config["agent_model_assignments"].get("default", "Not configured")

print(f"\n🤖 React Agent Model: {react_model}")
print(f"🔄 Default Model: {default_model}")

# Check environment variables
print("\n🔑 Environment Variables:")
env_vars = {
    "OPENROUTER_API_KEY": "✅ Set" if os.environ.get("OPENROUTER_API_KEY") else "❌ Not set",
    "SILICONFLOW_API_KEY": "✅ Set" if os.environ.get("SILICONFLOW_API_KEY") else "❌ Not set",
    "TAVILY_API_KEY": "✅ Set" if os.environ.get("TAVILY_API_KEY") else "❌ Not set",
    "REACT_AGENT_MODEL": os.environ.get("REACT_AGENT_MODEL", "Not set (will use config)")
}

for var, status in env_vars.items():
    print(f"  {var:25} {status}")

# Show available models
print("\n📚 Available Models:")
for model_name, model_config in config["model_configs"].items():
    api_key_env = model_config["api_key_env"]
    is_available = "✅" if os.environ.get(api_key_env) else "❌"
    print(f"  {is_available} {model_name:30} - {model_config['description']}")

print("\n" + "=" * 60)

# Final recommendation
if os.environ.get("OPENROUTER_API_KEY"):
    print("✅ System is configured to use GPT-OSS 120B via OpenRouter")
elif os.environ.get("SILICONFLOW_API_KEY"):
    print("⚠️  System will fall back to Qwen models via SiliconFlow")
    print("   For best performance, set OPENROUTER_API_KEY")
else:
    print("❌ No API keys configured! The system will not work.")
    print("   Please set either OPENROUTER_API_KEY or SILICONFLOW_API_KEY")

print("=" * 60)