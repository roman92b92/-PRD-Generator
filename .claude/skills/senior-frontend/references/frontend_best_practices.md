# Frontend Best Practices

## Overview

This guide covers patterns and practices for senior frontend developers, with emphasis on code organization, performance, and security.

## Patterns and Practices

### Pattern 1: Component Composition

**Description:**
Prefer composition over inheritance. Build small, focused components that do one thing well and compose them into complex UIs.

**When to Use:**
- Building reusable UI primitives
- Creating page layouts from shared components
- Sharing logic between components without prop-drilling

**Implementation:**
```typescript
// Compound component pattern
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card = ({ children, className }: CardProps) => (
  <div className={`card ${className ?? ''}`}>{children}</div>
);

Card.Header = ({ children }: { children: React.ReactNode }) => (
  <div className="card-header">{children}</div>
);

Card.Body = ({ children }: { children: React.ReactNode }) => (
  <div className="card-body">{children}</div>
);
```

**Benefits:**
- High reusability across the codebase
- Clear, readable JSX at call sites
- Easy to test in isolation

**Trade-offs:**
- More files/components to manage
- Can over-abstract simple UIs

---

### Pattern 2: Custom Hooks for Logic Extraction

**Description:**
Extract stateful logic into custom hooks to keep components lean and make logic testable independently.

**When to Use:**
- Fetching and caching data
- Managing form state
- Subscribing to browser events

**Implementation:**
```typescript
function useFetch<T>(url: string) {
  const [data, setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    fetch(url)
      .then(r => r.json())
      .then(d => { if (!cancelled) setData(d); })
      .catch(e => { if (!cancelled) setError(e); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [url]);

  return { data, loading, error };
}
```

**Benefits:**
- Logic is fully testable without rendering
- Components become pure view layers
- Easy to swap implementations

**Trade-offs:**
- Hooks rules can be tricky (no conditionals)
- Debugging requires React DevTools

---

## Guidelines

### Code Organization
- One component per file
- Co-locate tests with components (`Button.test.tsx` next to `Button.tsx`)
- Use barrel exports (`index.ts`) sparingly — avoid deep re-export chains
- Consistent naming: PascalCase components, camelCase hooks (`useMyHook`)

### Performance Considerations
- Memoize expensive computations with `useMemo`
- Stabilize callbacks with `useCallback` when passed as props
- Use `React.memo` for pure components rendered frequently
- Prefer CSS transitions over JS animations for 60fps performance
- Lazy-load routes and heavy components with `React.lazy`

### Security Best Practices
- Never `dangerouslySetInnerHTML` with user-supplied content
- Sanitize inputs before sending to APIs (use `zod` or `yup`)
- Store tokens in `httpOnly` cookies, not `localStorage`
- Apply `Content-Security-Policy` headers at the server level
- Validate file uploads (type, size) both client- and server-side

---

## Common Patterns

### Error Boundaries
Wrap feature sections in error boundaries to prevent full-page crashes.

```typescript
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    return this.state.hasError ? this.props.fallback : this.props.children;
  }
}
```

### Optimistic UI Updates
Update local state immediately, then reconcile with server response.

### Controlled vs Uncontrolled Inputs
Use controlled inputs (`value` + `onChange`) for forms that need validation. Use uncontrolled (`ref`) only for file inputs or when integrating with non-React libraries.

---

## Anti-Patterns to Avoid

### Prop Drilling Beyond 2 Levels
Pass data via Context or a state manager (Zustand, Redux) instead.

### Inline Object/Array Literals as Props
```tsx
// Bad — new reference every render
<Component style={{ color: 'red' }} items={[1, 2, 3]} />

// Good
const STYLE = { color: 'red' };
const ITEMS = [1, 2, 3];
<Component style={STYLE} items={ITEMS} />
```

### `useEffect` with Missing Dependencies
Always include every reactive value in the dependency array. Use `eslint-plugin-react-hooks` to enforce this.

---

## Tools and Resources

### Recommended Tools
- **ESLint + eslint-plugin-react-hooks**: Enforce rules of hooks and best practices
- **Prettier**: Consistent formatting across the team
- **Storybook**: Develop and document components in isolation
- **Playwright / Testing Library**: End-to-end and unit testing

### Further Reading
- [React Docs — Thinking in React](https://react.dev/learn/thinking-in-react)
- [web.dev Performance](https://web.dev/performance/)
- [OWASP Top 10 for Frontend](https://owasp.org/www-project-top-ten/)
