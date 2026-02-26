#!/usr/bin/env python3
"""
component_generator.py — Scaffold React/TypeScript components with best-practice structure.

Usage:
  python component_generator.py <target-path> [--verbose] [--json] [--output <file>]

Examples:
  python component_generator.py src/components/Button
  python component_generator.py src/features/auth/LoginForm --verbose
  python component_generator.py src/components --json --output report.json
"""

import argparse
import json
import os
import sys
from pathlib import Path


COMPONENT_TEMPLATE = '''\
import React from 'react';

interface {name}Props {{
  children?: React.ReactNode;
  className?: string;
}}

export function {name}({{ children, className }: {name}Props) {{
  return (
    <div className={{className}}>
      {{children}}
    </div>
  );
}}

export default {name};
'''

INDEX_TEMPLATE = '''\
export {{ {name}, default }} from './{name}';
'''

TEST_TEMPLATE = '''\
import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import {{ {name} }} from './{name}';

describe('{name}', () => {{
  it('renders children', () => {{
    render(<{name}>Hello</{name}>);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  }});
}});
'''

STORY_TEMPLATE = '''\
import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ {name} }} from './{name}';

const meta: Meta<typeof {name}> = {{
  title: 'Components/{name}',
  component: {name},
}};

export default meta;
type Story = StoryObj<typeof {name}>;

export const Default: Story = {{
  args: {{
    children: '{name} component',
  }},
}};
'''


class ComponentGenerator:
    def __init__(self, target: str, verbose: bool = False):
        self.target = Path(target)
        self.verbose = verbose
        self.findings: list[dict] = []

    def validate_target(self) -> bool:
        """Validate that the target path is usable."""
        if self.target.exists() and not self.target.is_dir():
            print(f"  Error: {self.target} exists and is not a directory.")
            return False
        return True

    def analyze(self) -> None:
        """Determine what files will be generated."""
        # Derive component name from the last path segment
        name = self.target.name
        if not name[0].isupper():
            name = name[0].upper() + name[1:]

        files = [
            (self.target / f"{name}.tsx", "component"),
            (self.target / "index.ts", "barrel export"),
            (self.target / f"{name}.test.tsx", "unit test"),
            (self.target / f"{name}.stories.tsx", "Storybook story"),
        ]

        for path, kind in files:
            status = "exists" if path.exists() else "will be created"
            self.findings.append({"file": str(path), "kind": kind, "status": status})
            if self.verbose:
                print(f"  {kind}: {path} ({status})")

        self._component_name = name

    def generate(self) -> None:
        """Write the scaffolded files."""
        name = self._component_name
        self.target.mkdir(parents=True, exist_ok=True)

        files = {
            self.target / f"{name}.tsx": COMPONENT_TEMPLATE.format(name=name),
            self.target / "index.ts": INDEX_TEMPLATE.format(name=name),
            self.target / f"{name}.test.tsx": TEST_TEMPLATE.format(name=name),
            self.target / f"{name}.stories.tsx": STORY_TEMPLATE.format(name=name),
        }

        for path, content in files.items():
            if not path.exists():
                path.write_text(content, encoding="utf-8")
                if self.verbose:
                    print(f"  Created: {path}")
            else:
                if self.verbose:
                    print(f"  Skipped (exists): {path}")

    def generate_report(self, as_json: bool = False) -> str:
        report = {
            "target": str(self.target),
            "component": getattr(self, "_component_name", ""),
            "status": "complete",
            "findings_count": len(self.findings),
            "findings": self.findings,
        }
        if as_json:
            return json.dumps(report, indent=2)
        lines = [
            f"Target:   {report['target']}",
            f"Component: {report['component']}",
            f"Status:   {report['status']}",
            f"Files:    {report['findings_count']}",
        ]
        for f in self.findings:
            lines.append(f"  [{f['kind']}] {f['file']} — {f['status']}")
        return "\n".join(lines)

    def run(self, generate: bool = True) -> None:
        """Execute the full workflow."""
        if not self.validate_target():
            sys.exit(1)
        self.analyze()
        if generate:
            self.generate()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a React/TypeScript component with tests and Storybook stories."
    )
    parser.add_argument("target", help="Path for the new component (e.g. src/components/Button)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write report to file")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, do not write files")
    args = parser.parse_args()

    print(f"\n  Component Generator")
    print(f"  Target: {args.target}\n")

    try:
        gen = ComponentGenerator(target=args.target, verbose=args.verbose)
        gen.run(generate=not args.dry_run)

        report = gen.generate_report(as_json=args.json)

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
