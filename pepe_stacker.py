import os
import sys
import requests
from datetime import datetime

# ========================================
# PEPE STACKER - GitHub Actions Version
# ========================================
API_KEY = os.environ.get("API_KEY")
AGENT_ID = os.environ.get("AGENT_ID")

FUND_NAME = "PEPE Stacker"
CURRENT_TOKEN = "0xc09C8242Eb21B24298303799Bb5Af402A2957777"
BASE_CURRENCY = "MON"
BUY_WEIGHT = 3                # 3% every 10 minutes
MIN_TRADE_SIZE_USD = 0.5

BASE_URL = "https://api.symphony.io"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def _get_headers():
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["x-api-key"] = API_KEY
    return h

def execute_buy():
    try:
        if not API_KEY or not AGENT_ID:
            log("❌ ERROR: API_KEY or AGENT_ID not set (execute_buy aborted).")
            return False

        # validate BUY_WEIGHT numeric and sensible
        try:
            weight_val = float(BUY_WEIGHT)
            if not (0 < weight_val <= 100):
                log(f"❌ ERROR: BUY_WEIGHT out of range (0,100]: {BUY_WEIGHT}")
                return False
        except Exception:
            log(f"❌ ERROR: BUY_WEIGHT is not numeric: {BUY_WEIGHT}")
            return False

        log(f"🔄 Accumulating {CURRENT_TOKEN} with {BUY_WEIGHT}% of {BASE_CURRENCY}")

        url = f"{BASE_URL}/agent/batch-swap"
        payload = {
            "agentId": AGENT_ID,
            "tokenIn": BASE_CURRENCY,
            "tokenOut": CURRENT_TOKEN,
            "weight": BUY_WEIGHT
        }

        response = requests.post(url, json=payload, headers=_get_headers(), timeout=30)

        # parse JSON safely
        try:
            result = response.json()
        except ValueError:
            result = None

        if response.ok:
            if isinstance(result, dict):
                successful = result.get("successful", 0)
                failed = result.get("failed", 0)

                if isinstance(successful, (int, float)) and successful > 0:
                    log(f"✅ Accumulated! {successful} swaps executed")
                    if failed and failed > 0:
                        log(f"⚠️  {failed} subscribers skipped - insufficient balance")
                    return True
                else:
                    log(f"❌ All swaps failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                # success but non-JSON response
                log(f"✅ API returned success (status {response.status_code})")
                return True
        else:
            body = result if result is not None else response.text
            log(f"❌ API error {response.status_code}: {body}")
            return False

    except requests.exceptions.Timeout:
        log("❌ Error: request timed out")
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
        sys.exit(1)

    success = execute_buy()

    if success:
        log("✅ Execution complete")
        log(f"🐸 Next stack in 10 minutes")
        log("=" * 60)
        sys.exit(0)
    else:
        log("❌ Execution failed")
        log("=" * 60)
        sys.exit(1)