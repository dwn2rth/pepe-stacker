import requests
import os
from datetime import datetime

# ========================================
# PEPE STACKER - GitHub Actions Version
# ========================================
API_KEY = os.environ.get("API_KEY")
AGENT_ID = os.environ.get("AGENT_ID")

# ========================================
# STRATEGY SETTINGS
# ========================================
FUND_NAME = "PEPE Stacker"
CURRENT_TOKEN = "0xc09C8242Eb21B24298303799Bb5Af402A2957777"
BASE_CURRENCY = "MON"
BUY_WEIGHT = 20                # 20% once daily
MIN_TRADE_SIZE_USD = 5

# ========================================
# CODE
# ========================================
BASE_URL = "https://api.symphony.io"
headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def execute_buy():
    try:
        log(f"🔄 Accumulating {CURRENT_TOKEN} with {BUY_WEIGHT}% of {BASE_CURRENCY}")
        
        url = f"{BASE_URL}/agent/batch-swap"
        payload = {
            "agentId": AGENT_ID,
            "tokenIn": BASE_CURRENCY,
            "tokenOut": CURRENT_TOKEN,
            "weight": BUY_WEIGHT
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            successful = result.get("successful", 0)
            failed = result.get("failed", 0)
            
            if successful > 0:
                log(f"✅ Accumulated! {successful} swaps executed")
                
                if failed > 0:
                    log(f"⚠️  {failed} subscribers skipped - insufficient balance")
                
                return True
            else:
                log(f"❌ All swaps failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            log(f"❌ API error: {result}")
            return False
            
    except Exception as e:
        log(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    log("=" * 60)
    log(f"🐸 {FUND_NAME} - Executing")
    log("=" * 60)
    
    if not API_KEY or not AGENT_ID:
        log("❌ ERROR: API_KEY or AGENT_ID not set!")
        exit(1)
    
    success = execute_buy()
    
    if success:
        log("✅ Execution complete")
        log(f"🐸 Next stack in 24 hours")
        log("=" * 60)
        exit(0)
    else:
        log("❌ Execution failed")
        log("=" * 60)
        exit(1)