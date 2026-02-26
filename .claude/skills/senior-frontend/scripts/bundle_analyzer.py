#!/usr/bin/env python3
"""
bundle_analyzer.py — Analyze Next.js / Webpack build output for bundle size issues.

Usage:
  python bundle_analyzer.py <build-dir> [--verbose] [--json] [--output <file>]

Examples:
  python bundle_analyzer.py .next
  python bundle_analyzer.py dist --verbose
  python bundle_analyzer.py .next --json --output bundle_report.json
"""

import argparse
import json
import os
import sys
from pathlib import Path


SIZE_WARN_KB = 250    # warn if a chunk exceeds this
SIZE_ERROR_KB = 500   # error if a chunk exceeds this


class BundleAnalyzer:
    def __init__(self, target: str, verbose: bool = False):
        self.target = Path(target)
        self.verbose = verbose
        self.findings: list[dict] = []

    def validate_target(self) -> bool:
        """Validate that the target build directory exists."""
        if not self.target.exists():
            print(f"  Error: {self.target} does not exist.")
            return False
        if not self.target.is_dir():
            print(f"  Error: {self.target} is not a directory.")
            return False
        return True

    def _scan_files(self) -> list[tuple[Path, int]]:
        """Collect all JS/CSS files and their sizes."""
        extensions = {".js", ".mjs", ".css"}
        files = []
        for root, _, names in os.walk(self.target):
            for name in names:
                p = Path(root) / name
                if p.suffix in extensions:
                    try:
                        size = p.stat().st_size
                        files.append((p, size))
                    except OSError:
                        pass
        return sorted(files, key=lambda x: x[1], reverse=True)

    def analyze(self) -> None:
        """Scan the build directory and identify large chunks."""
        files = self._scan_files()
        total_bytes = sum(s for _, s in files)

        if self.verbose:
            print(f"  Scanning {len(files)} files in {self.target}")

        for path, size_bytes in files:
            size_kb = size_bytes / 1024
            if size_kb >= SIZE_ERROR_KB:
                severity = "error"
            elif size_kb >= SIZE_WARN_KB:
                severity = "warning"
            else:
                severity = "ok"

            finding = {
                "file": str(path.relative_to(self.target)),
                "size_kb": round(size_kb, 1),
                "severity": severity,
            }
            self.findings.append(finding)

            if self.verbose or severity != "ok":
                icon = {"error": "x", "warning": "!", "ok": "v"}[severity]
                print(f"  [{icon}] {finding['file']} — {finding['size_kb']} KB ({severity})")

        self._total_kb = round(total_bytes / 1024, 1)
        self._file_count = len(files)

    def generate_report(self, as_json: bool = False) -> str:
        errors = [f for f in self.findings if f["severity"] == "error"]
        warnings = [f for f in self.findings if f["severity"] == "warning"]

        report = {
            "target": str(self.target),
            "status": "complete",
            "total_kb": getattr(self, "_total_kb", 0),
            "files_scanned": getattr(self, "_file_count", 0),
            "findings_count": len(self.findings),
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": self.findings,
            "recommendations": self._recommendations(errors, warnings),
        }

        if as_json:
            return json.dumps(report, indent=2)

        lines = [
            f"Target:        {report['target']}",
            f"Total size:    {report['total_kb']} KB",
            f"Files scanned: {report['files_scanned']}",
            f"Errors:        {report['errors']}",
            f"Warnings:      {report['warnings']}",
        ]
        if report["recommendations"]:
            lines.append("\nRecommendations:")
            for rec in report["recommendations"]:
                lines.append(f"  - {rec}")
        return "\n".join(lines)

    def _recommendations(self, errors: list, warnings: list) -> list[str]:
        recs = []
        if errors:
            recs.append(
                f"{len(errors)} chunk(s) exceed {SIZE_ERROR_KB} KB. "
                "Use dynamic import() to code-split large dependencies."
            )
        if warnings:
            recs.append(
                f"{len(warnings)} chunk(s) exceed {SIZE_WARN_KB} KB. "
                "Consider lazy-loading or tree-shaking these modules."
            )
        if not errors and not warnings:
            recs.append("Bundle looks healthy! No chunks exceed the size thresholds.")
        recs.append("Run `npx @next/bundle-analyzer` for a visual treemap.")
        return recs

    def run(self) -> None:
        """Execute the full analysis workflow."""
        if not self.validate_target():
            sys.exit(1)
        self.analyze()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a Next.js/.next build directory for large bundle chunks."
    )
    parser.add_argument("target", help="Path to build directory (e.g. .next or dist)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show all files, not just issues")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write report to file")
    args = parser.parse_args()

    print(f"\n  Bundle Analyzer")
    print(f"  Target: {args.target}\n")

    try:
        analyzer = BundleAnalyzer(target=args.target, verbose=args.verbose)
        analyzer.run()

        report = analyzer.generate_report(as_json=args.json)

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
