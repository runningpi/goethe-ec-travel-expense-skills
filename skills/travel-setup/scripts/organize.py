"""Rename / archive the files of a trip folder according to a plan - only after the user agreed.

  python organize.py --folder <trip folder> --plan plan.json            (dry run: prints the plan)
  python organize.py --folder <trip folder> --plan plan.json --apply

plan.json: [["old name", "new name"], ["unused.pdf", "Archiv/unused.pdf"], ...]
Nothing is ever deleted. The script refuses to run if a source is missing or a target
already exists, and it warns about files in the folder the plan does not mention.
Remember to point any later re-runs (assemble spec) at the new names.
"""
import argparse
import json
import os

from common import ensure_utf8_stdout


def main():
    ensure_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    plan = json.load(open(a.plan, encoding="utf-8"))
    errors = []
    for old, new in plan:
        if not os.path.isfile(os.path.join(a.folder, old)):
            errors.append(f"missing: {old}")
        if os.path.exists(os.path.join(a.folder, new)):
            errors.append(f"target exists: {new}")
    if len({n for _, n in plan}) != len(plan):
        errors.append("two files would get the same new name")
    if errors:
        raise SystemExit("\n".join(errors))
    planned = {o for o, _ in plan}
    unplanned = [f for f in os.listdir(a.folder)
                 if os.path.isfile(os.path.join(a.folder, f)) and f not in planned]
    for old, new in plan:
        print(f"{old}  ->  {new}")
    if unplanned:
        print("\nNot in the plan (stay where they are):", unplanned)
    if not a.apply:
        print("\nDry run. Re-run with --apply after the user confirmed.")
        return
    for old, new in plan:
        dst = os.path.join(a.folder, new)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(os.path.join(a.folder, old), dst)
    print(f"\nDone: {len(plan)} files moved/renamed.")


if __name__ == "__main__":
    main()
