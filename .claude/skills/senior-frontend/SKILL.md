# Senior Frontend Skill Documentation

This comprehensive resource provides modern frontend development capabilities centered on ReactJS, NextJS, and TypeScript. The toolkit includes three primary automated scripts for component generation, bundle analysis, and project scaffolding.

## Core Tools

The skill offers three main capabilities:

1. **Component Generator** (`scripts/component_generator.py`) — Automates component scaffolding with built-in quality checks and configurable templates

2. **Bundle Analyzer** (`scripts/bundle_analyzer.py`) — Provides performance metrics and optimization recommendations with automated fixes

3. **Frontend Scaffolder** (`scripts/frontend_scaffolder.py`) — Delivers production-grade automation for specialized frontend tasks

## Documentation Resources

Three reference guides support development work:

- `references/react_patterns.md` — React patterns covering established approaches and anti-patterns
- `references/nextjs_optimization_guide.md` — NextJS optimization documentation with performance tuning strategies
- `references/frontend_best_practices.md` — Frontend best practices addressing technology configuration and security

## Technology Support

The stack encompasses:
- **Languages**: TypeScript, JavaScript
- **Frameworks**: React, Next.js
- **Backend**: Node.js
- **Deployment**: Docker, Kubernetes, AWS, GCP

## Development Approach

Key practices:
- Run quality checks before shipping
- Follow documented patterns from references/
- Implement security validations (input validation, auth)
- Keep dependencies current
- **Measure before optimizing**

## Usage

### Component Generator
```bash
python scripts/component_generator.py <target-path> [--verbose] [--json] [--output <file>]
```

### Bundle Analyzer
```bash
python scripts/bundle_analyzer.py <target-path> [--verbose] [--json] [--output <file>]
```

### Frontend Scaffolder
```bash
python scripts/frontend_scaffolder.py <target-path> [--verbose] [--json] [--output <file>]
```

## When to Use This Skill

- Building new React/Next.js components or pages
- Optimizing bundle size and performance
- Scaffolding production-grade frontend projects
- Code reviews focused on frontend architecture
- Migrating from class components to hooks
- Implementing SSR/SSG patterns in Next.js
