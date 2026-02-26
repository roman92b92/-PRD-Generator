# React Patterns

## Overview

This reference guide provides comprehensive patterns for senior frontend developers building production React applications.

## Patterns and Practices

### Pattern 1: Render Props / Children as Function

**Description:**
Pass a function as `children` (or a named prop) to allow the parent component to control what gets rendered, enabling maximum flexibility.

**When to Use:**
- Sharing stateful logic without HOCs
- Building headless UI components
- Giving consumers full rendering control

**Implementation:**
```typescript
interface MouseTrackerProps {
  children: (pos: { x: number; y: number }) => React.ReactNode;
}

export function MouseTracker({ children }: MouseTrackerProps) {
  const [pos, setPos] = React.useState({ x: 0, y: 0 });
  const handleMove = (e: React.MouseEvent) =>
    setPos({ x: e.clientX, y: e.clientY });
  return <div onMouseMove={handleMove}>{children(pos)}</div>;
}

// Usage
<MouseTracker>
  {({ x, y }) => <p>Mouse is at {x}, {y}</p>}
</MouseTracker>
```

**Benefits:**
- Full rendering control for consumers
- No wrapper component in the tree
- Easy to compose with other patterns

**Trade-offs:**
- Nested callbacks can reduce readability
- Custom hooks often achieve the same result more cleanly

---

### Pattern 2: Context + Reducer (Mini Redux)

**Description:**
Combine `useContext` and `useReducer` for predictable shared state without a third-party library.

**Implementation:**
```typescript
type Action = { type: 'increment' } | { type: 'decrement' };

interface State { count: number }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 };
    case 'decrement': return { count: state.count - 1 };
  }
}

const CounterContext = React.createContext<{
  state: State;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export function CounterProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = React.useReducer(reducer, { count: 0 });
  return (
    <CounterContext.Provider value={{ state, dispatch }}>
      {children}
    </CounterContext.Provider>
  );
}

export function useCounter() {
  const ctx = React.useContext(CounterContext);
  if (!ctx) throw new Error('useCounter must be used within CounterProvider');
  return ctx;
}
```

**Benefits:**
- Zero dependencies
- Predictable state transitions
- Easy to test reducer in isolation

**Trade-offs:**
- Context re-renders all consumers on every dispatch
- Not suitable for high-frequency updates (use Zustand/Jotai instead)

---

### Pattern 3: Suspense + Lazy Loading

**Description:**
Defer loading of heavy components until they're needed, improving initial bundle size.

**Implementation:**
```typescript
const HeavyChart = React.lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <React.Suspense fallback={<Skeleton />}>
      <HeavyChart />
    </React.Suspense>
  );
}
```

---

## Guidelines

### Code Organization
- Clear structure: features/, components/, hooks/, utils/, types/
- Logical separation: keep API calls out of components
- Consistent naming: PascalCase for components, camelCase for everything else
- Proper documentation: JSDoc for public APIs

### Performance Considerations
- Optimization strategies: virtualize long lists (`react-window`)
- Bottleneck identification: React DevTools Profiler
- Monitoring approaches: Web Vitals (CLS, LCP, FID)
- Scaling techniques: code splitting by route

### Security Best Practices
- Input validation: `zod` schemas at boundaries
- Authentication: httpOnly cookies for tokens
- Authorization: check permissions server-side, mirror client-side for UX only
- Data protection: never log sensitive fields (passwords, tokens)

---

## Common Patterns

### Pattern A: HOC (Higher-Order Component)
Wraps a component to inject props or behavior. Useful for cross-cutting concerns like auth guards.

```typescript
function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthGuard(props: P) {
    const { user } = useAuth();
    if (!user) return <Navigate to="/login" />;
    return <Component {...props} />;
  };
}
```

### Pattern B: Controlled Form with Validation
Use `react-hook-form` + `zod` resolver for type-safe forms:

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({ email: z.string().email() });

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });
  return (
    <form onSubmit={handleSubmit(console.log)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
    </form>
  );
}
```

### Pattern C: Zustand Store
Lightweight global state with minimal boilerplate:

```typescript
import { create } from 'zustand';

interface Store { count: number; increment: () => void }

const useStore = create<Store>(set => ({
  count: 0,
  increment: () => set(s => ({ count: s.count + 1 })),
}));
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Mutating State Directly
```typescript
// Bad
state.items.push(newItem); // React won't re-render

// Good
setState(prev => ({ ...prev, items: [...prev.items, newItem] }));
```

### Anti-Pattern 2: `useEffect` for Derived State
If a value can be computed from existing state/props, compute it inline — don't sync it with `useEffect`.

---

## Tools and Resources

### Recommended Tools
- **react-query / TanStack Query**: Server state management
- **react-hook-form**: Performant forms
- **Zustand**: Lightweight client state

### Further Reading
- [React Docs](https://react.dev)
- [TanStack Query](https://tanstack.com/query)
- [Zustand](https://github.com/pmndrs/zustand)

## Conclusion

Apply these patterns contextually. Custom hooks solve most problems that render props and HOCs once solved. Reach for context + reducer before third-party state management. Always measure performance before optimizing.
