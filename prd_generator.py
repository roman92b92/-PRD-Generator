"""
prd_generator.py — Core PRD generation engine using the Anthropic Claude API.

Supports four PRD formats:
  - standard      : Full 11-section PRD for complex features
  - one_page      : Concise single-page PRD for quick alignment
  - agile_epic    : Sprint-based agile epic format
  - feature_brief : Lightweight hypothesis-driven exploration brief
"""

import anthropic
from datetime import datetime
from typing import Iterator


# ---------------------------------------------------------------------------
# System prompt — instructs Claude to behave as a senior PM
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a Principal Product Manager at a top-tier tech company with 15 years of \
experience shipping products used by millions. You write world-class Product Requirements Documents \
(PRDs) adopted as the gold standard at FAANG companies.

Your PRDs are:
- **Specific**: Concrete details, not vague descriptions or placeholders
- **Measurable**: Every goal has a numeric target metric
- **Actionable**: Engineers can implement directly from your requirements
- **Complete**: No section is left with a placeholder — generate real content
- **Realistic**: Timelines, estimates and metrics are grounded in reality

Rules you must ALWAYS follow:
1. Fill ALL sections with specific, realistic content based on the product inputs
2. Generate believable success metrics (e.g. "Increase checkout conversion from 64% → 78%")
3. Write 4–6 concrete user stories with acceptance criteria checklists
4. List 6+ functional requirements ranked by priority (P0/P1/P2)
5. Identify 3–5 risks with specific, actionable mitigations
6. Propose a realistic timeline with clear week-by-week milestones
7. Always define explicit out-of-scope items to prevent scope creep
8. Use clean, professional Markdown throughout
9. NEVER write "[describe here]", "[add details]" or any placeholder text
"""

# ---------------------------------------------------------------------------
# PRD template prompts
# ---------------------------------------------------------------------------

TEMPLATES: dict[str, str] = {

    "standard": """\
Using the product information above, generate a complete, production-quality Standard PRD. \
Fill EVERY section with specific, detailed, realistic content — no placeholders.

---

# {product_name}
### Product Requirements Document

| | |
|---|---|
| **Version** | 1.0 |
| **Date** | {date} |
| **Status** | Draft |
| **Author** | [PM Name] |

---

## 1. Executive Summary

*(One-paragraph overview covering the problem, solution, business impact and key metrics)*

## 2. Problem Definition

### 2.1 Customer Problem
*(Who is affected, what specifically hurts them, how often, why it matters now)*

### 2.2 Market Opportunity
*(Market size, competitive landscape, why now is the right time)*

### 2.3 Business Case
*(Revenue potential, cost savings, strategic alignment, cost of inaction)*

## 3. Solution Overview

### 3.1 Proposed Solution
*(What we are building, key capabilities, how users experience it)*

### 3.2 In Scope
*(Bullet list of features explicitly included in this release)*

### 3.3 Out of Scope
*(Bullet list of things we are explicitly NOT building — this prevents scope creep)*

### 3.4 MVP Definition
*(Minimum viable feature set, success criteria, learning goals)*

## 4. User Stories & Requirements

### 4.1 User Stories
*(4–6 stories in "As a [persona]… I want… So that…" format, each with an acceptance criteria checklist)*

### 4.2 Functional Requirements
*(Table: ID | Requirement | Priority | Notes — at least 6 rows)*

### 4.3 Non-Functional Requirements
*(Performance targets, scalability, security, reliability, accessibility)*

## 5. Design & User Experience

### 5.1 Design Principles
*(3 core principles guiding this feature)*

### 5.2 Key Screens & Flows
*(Describe the main user flows step by step)*

## 6. Technical Specifications

### 6.1 Architecture Overview
*(High-level system architecture and key components)*

### 6.2 API / Integration Points
*(Any new or modified endpoints, third-party integrations)*

### 6.3 Data Model
*(Key entities and their relationships)*

### 6.4 Security & Compliance
*(Auth model, data encryption, PII handling, regulatory notes)*

## 7. Go-to-Market Strategy

### 7.1 Launch Plan
*(Phased rollout: beta → limited → general availability)*

### 7.2 Success Metrics
*(Table: Metric | Current Baseline | Target | Measurement Method)*

## 8. Risks & Mitigations

*(Table: Risk | Probability | Impact | Mitigation Strategy — at least 4 rows)*

## 9. Timeline & Milestones

*(Table: Milestone | Target Week | Deliverables | Success Criteria)*

## 10. Team & Resources

*(Engineering, design, QA headcount; budget estimate)*

## 11. Open Questions

*(Numbered list of unresolved questions that need answers before development starts)*
""",

    "one_page": """\
Using the product information above, generate a crisp, complete One-Page PRD. \
Every field must contain specific, realistic content — no placeholders.

---

# {product_name}
### One-Page PRD

**Date**: {date} &nbsp;|&nbsp; **Status**: Draft

---

## Problem
*(2–3 sentences: what problem, for whom, and why it matters)*

## Solution
*(2–3 sentences: what we are building and how it solves the problem)*

## Why Now?
*(3 bullet points explaining urgency)*

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| *(KPI 1)* | | |
| *(KPI 2)* | | |
| *(KPI 3)* | | |

## Scope
**In**: *(comma-separated feature list)*
**Out**: *(explicit exclusions)*

## User Flow
```
[Step 1] → [Step 2] → [Step 3] → ✓ Done
```

## Risks
1. *(Risk)* → *(Mitigation)*
2. *(Risk)* → *(Mitigation)*

## Timeline
| Phase | Duration |
|-------|----------|
| Design | |
| Development | |
| Testing | |
| Launch | |

## Resources
*(Engineering, design, QA headcount)*

## Open Questions
1. *(Question?)*
""",

    "agile_epic": """\
Using the product information above, generate a complete Agile Epic PRD. \
Fill every section with specific, realistic content — no placeholders.

---

# {product_name}
### Agile Epic

| | |
|---|---|
| **Epic ID** | EPIC-001 |
| **Quarter** | {quarter} |
| **Status** | Discovery |

---

## Problem Statement
*(2–3 sentences)*

## Goals & Objectives
1. *(Objective 1)*
2. *(Objective 2)*
3. *(Objective 3)*

## Success Metrics
| Metric | Target | How Measured |
|--------|--------|--------------|
| | | |

## User Story Map

| Story ID | User Story | Priority | Story Points | Status |
|----------|-----------|----------|--------------|--------|
| US-001 | As a… | P0 | | To Do |
| US-002 | As a… | P0 | | To Do |
| US-003 | As a… | P1 | | To Do |
| US-004 | As a… | P1 | | To Do |

## Sprint Breakdown
*(Propose a 2-sprint delivery plan with specific deliverables per sprint)*

## Dependencies
*(List teams or systems this epic depends on)*

## Acceptance Criteria
- [ ] *(Criterion 1)*
- [ ] *(Criterion 2)*
- [ ] *(Criterion 3)*
- [ ] Performance targets met
- [ ] Security review passed

## Definition of Done
*(Complete checklist for epic closure)*

## Risks & Blockers
*(Known risks that could affect delivery)*
""",

    "feature_brief": """\
Using the product information above, generate a complete Feature Brief. \
Fill every field with specific, realistic content — no placeholders.

---

# {product_name}
### Feature Brief

**Date**: {date}

---

## Context
*(Why are we considering this? What triggered this exploration?)*

## Hypothesis
> We believe that **[building this feature]**
> for **[these users]**
> will **[achieve this specific outcome]**.
> We'll know we're right when **[we observe this measurable signal]**.

## Proposed Approach
*(High-level approach in 4–6 sentences)*

## Key Assumptions
*(List the assumptions this brief rests on — what do we need to validate?)*

## Effort Estimate
- **Size**: *(XS / S / M / L / XL)*
- **Confidence**: *(High / Medium / Low)*
- **Rough Timeline**: *(e.g. 2 sprints)*

## Success Signal
*(What single metric would tell us this feature worked?)*

## Alternatives Considered
*(What other approaches did we reject and why?)*

## Next Steps
- [ ] User research / interviews
- [ ] Design exploration
- [ ] Technical spike
- [ ] Stakeholder review
- [ ] Decision: build / shelve / revisit
""",
}


# ---------------------------------------------------------------------------
# Generator class
# ---------------------------------------------------------------------------

class PRDGenerator:
    """Generates Product Requirements Documents using the Claude API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _format_template(self, format_type: str) -> str:
        now = datetime.now()
        quarter = f"Q{(now.month - 1) // 3 + 1} {now.year}"
        date = now.strftime("%B %d, %Y")
        template = TEMPLATES.get(format_type, TEMPLATES["standard"])
        # product_name placeholder filled by the prompt builder, not here
        return template.replace("{date}", date).replace("{quarter}", quarter)

    def _build_prompt(self, inputs: dict, format_type: str) -> str:
        product_name = inputs.get("product_name", "Untitled Feature")
        template = self._format_template(format_type).replace(
            "{product_name}", product_name
        )

        return f"""## Product Inputs

**Product / Feature Name**: {product_name}

**Problem Statement**:
{inputs.get("problem_statement", "").strip()}

**Target Users**:
{inputs.get("target_users", "").strip()}

**Proposed Solution**:
{inputs.get("proposed_solution", "").strip()}

**Business Goals & Expected Impact**:
{inputs.get("business_goals", "").strip()}

**Timeline**:
{inputs.get("timeline", "To be determined").strip()}

**Additional Context**:
{inputs.get("additional_context", "None provided").strip()}

---

{template}

Generate the complete PRD now. Replace every placeholder with specific, realistic, \
actionable content derived from the product inputs above."""

    # ------------------------------------------------------------------
    # Internal: build message content (text + optional images)
    # ------------------------------------------------------------------

    def _build_content(self, inputs: dict, format_type: str, images: list) -> list | str:
        """
        Build the user message content.

        With no images: returns a plain string (backward compatible).
        With images: returns a content block list:
          [text intro, image_1, …, image_N, text prompt]
        """
        prompt = self._build_prompt(inputs, format_type)

        if not images:
            return prompt

        n = len(images)
        intro = (
            f"I'm providing {n} visual reference{'s' if n > 1 else ''} "
            f"(mockup{'s' if n > 1 else ''} / wireframe{'s' if n > 1 else ''}) "
            f"to inform this PRD.\n\n"
            f"Please:\n"
            f"1. Carefully analyze each visual and identify key screens, user flows, "
            f"and UI patterns shown.\n"
            f"2. Reference specific observations from the visuals in the relevant PRD "
            f"sections (e.g. Design & UX, User Stories, Functional Requirements).\n"
            f"3. Use the visuals to make the acceptance criteria and functional "
            f"requirements more precise and implementation-ready.\n\n"
        )

        content: list = [{"type": "text", "text": intro}]

        for img in images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img.get("media_type", "image/png"),
                    "data": img["data"],
                },
            })

        content.append({"type": "text", "text": prompt})
        return content

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_stream(
        self,
        inputs: dict,
        format_type: str = "standard",
        images: list | None = None,
    ) -> Iterator[str]:
        """Stream the PRD, yielding text chunks as they arrive.

        Args:
            inputs:      Form fields dict (product_name, problem_statement, …)
            format_type: One of standard | one_page | agile_epic | feature_brief
            images:      Optional list of {data: <base64>, media_type: <mime>}
        """
        content = self._build_content(inputs, format_type, images or [])

        with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        ) as stream:
            for text in stream.text_stream:
                yield text

    def generate(
        self,
        inputs: dict,
        format_type: str = "standard",
        images: list | None = None,
    ) -> str:
        """Generate a complete PRD and return it as a string."""
        return "".join(self.generate_stream(inputs, format_type, images))


# ---------------------------------------------------------------------------
# CLI entry point (optional)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json, sys, os

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key and os.path.exists("config.json"):
        with open("config.json") as f:
            api_key = json.load(f).get("api_key")

    if not api_key:
        print("Error: set ANTHROPIC_API_KEY or add api_key to config.json")
        sys.exit(1)

    sample = {
        "product_name": "Smart Notification Center",
        "problem_statement": (
            "Users receive too many notifications and miss critical alerts. "
            "Our current system sends all notifications with equal priority, "
            "causing notification fatigue and a 23% drop in engagement."
        ),
        "target_users": "Mobile app users, enterprise dashboard users, product managers",
        "proposed_solution": (
            "An AI-powered notification center that intelligently groups, "
            "prioritizes, and summarizes notifications based on user behavior "
            "and explicit preferences."
        ),
        "business_goals": (
            "Increase notification open rate from 18% to 35%, "
            "reduce unsubscribe rate by 40%, improve DAU retention by 15%."
        ),
        "timeline": "Q3 2026 launch (12 weeks)",
        "additional_context": "Mobile-first, iOS and Android parity required.",
    }

    gen = PRDGenerator(api_key)
    print("\n--- Generating Standard PRD (streaming) ---\n")
    for chunk in gen.generate_stream(sample, "standard"):
        print(chunk, end="", flush=True)
    print("\n\n--- Done ---")
