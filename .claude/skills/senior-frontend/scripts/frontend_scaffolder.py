#!/usr/bin/env python3
"""
frontend_scaffolder.py — Scaffold production-grade frontend project structures.

Usage:
  python frontend_scaffolder.py <target-dir> [--verbose] [--json] [--output <file>]

Examples:
  python frontend_scaffolder.py my-app
  python frontend_scaffolder.py src/features/auth --verbose
  python frontend_scaffolder.py my-app --json --output scaffold_report.json
"""

import argparse
import json
import os
import sys
from pathlib import Path


FEATURE_STRUCTURE = {
    "components": ["index.ts"],
    "hooks": ["index.ts"],
    "types": ["index.ts"],
    "utils": ["index.ts"],
    "api": ["index.ts"],
    "__tests__": [],
}

GITKEEP = ""  # empty placeholder file

INDEX_BARREL = "// Re-export public API\n"

TSCONFIG_SNIPPET = """\
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
"""

ESLINT_CONFIG = """\
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "react-hooks/exhaustive-deps": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
"""


class FrontendScaffolder:
    def __init__(self, target: str, verbose: bool = False):
        self.target = Path(target)
        self.verbose = verbose
        self.findings: list[dict] = []

    def validate_target(self) -> bool:
        """Validate the target path exists and is accessible."""
        if self.target.exists() and not self.target.is_dir():
            print(f"  Error: {self.target} is not a directory.")
            return False
        return True

    def analyze(self) -> None:
        """Determine what directories and files will be created."""
        for folder, files in FEATURE_STRUCTURE.items():
            dir_path = self.target / folder
            status = "exists" if dir_path.exists() else "will be created"
            self.findings.append({"type": "directory", "path": str(dir_path), "status": status})
            if self.verbose:
                print(f"  dir: {dir_path} ({status})")

            for fname in files:
                fpath = dir_path / fname
                fstatus = "exists" if fpath.exists() else "will be created"
                self.findings.append({"type": "file", "path": str(fpath), "status": fstatus})
                if self.verbose:
                    print(f"    file: {fpath} ({fstatus})")

    def scaffold(self) -> None:
        """Create the directory and file structure."""
        self.target.mkdir(parents=True, exist_ok=True)

        for folder, files in FEATURE_STRUCTURE.items():
            dir_path = self.target / folder
            dir_path.mkdir(exist_ok=True)

            for fname in files:
                fpath = dir_path / fname
                if not fpath.exists():
                    fpath.write_text(INDEX_BARREL, encoding="utf-8")
                    if self.verbose:
                        print(f"  Created: {fpath}")

            # Add .gitkeep to empty test dirs
            if not files:
                gitkeep = dir_path / ".gitkeep"
                if not gitkeep.exists():
                    gitkeep.write_text(GITKEEP, encoding="utf-8")

        if self.verbose:
            print(f"\n  Scaffold complete: {self.target}")

    def generate_report(self, as_json: bool = False) -> str:
        dirs_created = sum(1 for f in self.findings if f["type"] == "directory" and f["status"] == "will be created")
        files_created = sum(1 for f in self.findings if f["type"] == "file" and f["status"] == "will be created")

        report = {
            "target": str(self.target),
            "status": "complete",
            "findings_count": len(self.findings),
            "directories_created": dirs_created,
            "files_created": files_created,
            "findings": self.findings,
        }

        if as_json:
            return json.dumps(report, indent=2)

        lines = [
            f"Target:              {report['target']}",
            f"Status:              {report['status']}",
            f"Directories created: {report['directories_created']}",
            f"Files created:       {report['files_created']}",
        ]
        return "\n".join(lines)

    def run(self, scaffold: bool = True) -> None:
        """Execute validation, analysis, and optional scaffolding."""
        if not self.validate_target():
            sys.exit(1)
        self.analyze()
        if scaffold:
            self.scaffold()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a production-grade frontend feature directory structure."
    )
    parser.add_argument("target", help="Target directory (e.g. src/features/auth or my-app)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write report to file")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, do not write files")
    args = parser.parse_args()

    print(f"\n  Frontend Scaffolder")
    print(f"  Target: {args.target}\n")

    try:
        scaffolder = FrontendScaffolder(target=args.target, verbose=args.verbose)
        scaffolder.run(scaffold=not args.dry_run)

        report = scaffolder.generate_report(as_json=args.json)

        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
            print(f"\n  Report written to {args.output}")
        else:
            print(f"\n{report}")

        print(f"\n  Done.")
    except Exception as exc:
        print(f"\n  Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
