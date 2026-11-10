"""Archive artifacts and record metrics from a completed real eval run."""
import argparse
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--changed", default="system_prompt.md")
    args = parser.parse_args()
    run = json.loads(args.run.read_text(encoding="utf-8"))
    archive = ROOT / "artifacts" / "versions" / run["version"]
    archive.mkdir(parents=True, exist_ok=True)
    for key, name in [("system_prompt", "system_prompt.md"), ("tools", "tools.yaml")]:
        source = Path(run[key])
        if not (archive / name).exists():
            shutil.copyfile(source, archive / name)
    log = ROOT / "artifacts" / "version_log.csv"
    with log.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    row = {key: run.get(key, "") for key in ["version", "artifact_version", "prompt_hash", "tools_hash"]}
    row.update(author="Nguyen Thanh Liem", changed_artifact=args.changed,
               reason=f"Real API eval; {run['provider']}/{run['model']}", hypothesis=args.hypothesis,
               metric_before=rows[-1]["metric_after"] if rows else "",
               metric_after=run["summary"]["case_accuracy"], run_file=str(args.run.relative_to(ROOT) if args.run.is_absolute() else args.run))
    rows.append(row)
    with log.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    main()
