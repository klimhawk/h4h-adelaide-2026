"""Headless acceptance checks for app.py (A5 to A9) using Streamlit's AppTest.

Gemma is replaced by a fake client that counts calls, so no API key is used or needed.
Run: .venv/bin/python tests/check_app.py
"""

import os
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")
CALLS = []
FAIL_NEXT = []  # push a status code to make the next call raise


class FakeServerError(Exception):
    def __init__(self, code):
        super().__init__(f"{code} INTERNAL")
        self.code = code


class FakeModels:
    def generate_content(self, model, contents, config=None):
        CALLS.append((model, contents, config))
        if FAIL_NEXT:
            raise FakeServerError(FAIL_NEXT.pop())
        return type("R", (), {"text": "FAKE GEMMA ANSWER"})()


class FakeClient:
    def __init__(self, api_key):
        self.models = FakeModels()


import google.genai  # noqa: E402

google.genai.Client = FakeClient
os.environ["GEMINI_API_KEY"] = "test-placeholder"


def texts(at):
    return " | ".join([m.value for m in at.markdown] + [w.value for w in at.warning] + [i.value for i in at.info])


def submit(at, value):
    at.text_input(key="pc_input").set_value(value).run()
    return at


results = []


def check(name, ok, seen):
    results.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'} {name}: {seen}")


at = AppTest.from_file(APP, default_timeout=60).run()
check("A1 start", not at.exception, f"exceptions={len(at.exception)}")

for bad in ["abc", "123", " 12a4 "]:
    submit(at, bad)
    check(f"A9 bad input {bad!r}", "Please enter a 4-digit postcode" in texts(at) and not CALLS, f"calls={len(CALLS)}")

submit(at, " 5159 ")
t = texts(at)
card_ok = all(s in t for s in ["Postcode 5159", "1,162", "1st of 347", "Explained by Gemma 4", "FAKE GEMMA ANSWER"])
check("A6 leader card + Gemma box (spaces trimmed)", card_ok and len(CALLS) == 1, f"calls={len(CALLS)}")
prompt = CALLS[0][1] if CALLS else ""
check("A6 model and prompt facts", CALLS and CALLS[0][0] == "gemma-4-26b-a4b-it"
      and "postcode 5159" in prompt and "rank 1 of 347" in prompt and "SA median 10.5" in prompt
      and CALLS[0][2].thinking_config.thinking_level.name == "MINIMAL", prompt[:400])

submit(at, "5114")
submit(at, "5159")
check("A7 repeat makes no new call", len(CALLS) == 2, f"calls after 5159,5114,5159 = {len(CALLS)}")

before = len(CALLS)
submit(at, "5001")
t = texts(at)
check("A8 no-data postcode: plain message, no call", len(CALLS) == before and "no ABS postal area" in t
      and "Disadvantage decile: <b>no data</b>" in t, f"calls={len(CALLS)}")

submit(at, "5111")
check("NO_DECILE postcode calls Gemma with decile 'no data'", len(CALLS) == before + 1
      and "disadvantage decile no data" in CALLS[-1][1], CALLS[-1][1][-260:] if CALLS else "")

before = len(CALLS)
submit(at, "3000")
check("Not in SA data: plain message, no call", len(CALLS) == before and "not in the South Australian data" in texts(at), f"calls={len(CALLS)}")

before = len(CALLS)
FAIL_NEXT.append(500)
submit(at, "5038")
t = texts(at)
retry = [b for b in at.button if b.label == "Try again"]
check("Gemma 500: fallback, server-error note, Try again button", len(CALLS) == before + 1
      and "Gemma is not available right now" in t and "server error (500)" in t and bool(retry), f"calls={len(CALLS)}")
at.run()
check("Failure not re-called on rerun", len(CALLS) == before + 1, f"calls={len(CALLS)}")
retry[0].click().run()
t = texts(at)
check("Try again makes one call and shows answer", len(CALLS) == before + 2 and "FAKE GEMMA ANSWER" in t
      and "Answered in" in t and not [b for b in at.button if b.label == "Try again"], f"calls={len(CALLS)}")

cap = [m.value for m in at.markdown if "deciles 8 to 10" in m.value]
check("A5 caption present", bool(cap), cap[0] if cap else "missing")
check("A10 footer", any("Snowflake Marketplace rows are not redistributed" in c.value and "CC BY 4.0" in c.value
                        and "Gemma 4 through the Gemini API" in c.value for c in at.caption), "")

print(f"\n{sum(ok for _, ok in results)}/{len(results)} passed")
sys.exit(0 if all(ok for _, ok in results) else 1)
