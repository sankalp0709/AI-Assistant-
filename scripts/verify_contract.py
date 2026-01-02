import argparse
import json
import sys
import os
from typing import List

REQUIRED = ["assistant_message", "action_taken", "next_steps", "confidence_level", "trace_id", "response_version"]
CONF_ENUM = {"high", "medium", "low"}

def verify_obj(obj: dict) -> List[str]:
    errors = []
    for k in REQUIRED:
        if k not in obj:
            errors.append(f"missing:{k}")
    if "response_version" in obj and obj["response_version"] != "v1":
        errors.append("invalid:response_version")
    if "confidence_level" in obj and obj["confidence_level"] not in CONF_ENUM:
        errors.append("invalid:confidence_level")
    if "next_steps" in obj and not isinstance(obj["next_steps"], list):
        errors.append("invalid:next_steps_type")
    if "assistant_message" in obj and not isinstance(obj["assistant_message"], str):
        errors.append("invalid:assistant_message_type")
    if "action_taken" in obj and not isinstance(obj["action_taken"], str):
        errors.append("invalid:action_taken_type")
    if "trace_id" in obj and not isinstance(obj["trace_id"], str):
        errors.append("invalid:trace_id_type")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    path = os.path.abspath(args.file)
    with open(path, "r") as f:
        data = json.load(f)
    if isinstance(data, dict):
        items = [data]
    else:
        items = data
    ok = True
    for i, obj in enumerate(items):
        errs = verify_obj(obj)
        if errs:
            ok = False
            print(f"[FAIL] index={i} errors={','.join(errs)}")
        else:
            print(f"[OK] index={i}")
    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
