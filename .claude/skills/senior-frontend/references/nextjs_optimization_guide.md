# Next.js Optimization Guide

## Overview

This reference covers performance optimization strategies for production Next.js applications, from rendering strategies to bundle analysis and Core Web Vitals.

## Rendering Strategies

### Pattern 1: Static Site Generation (SSG) with ISR

**Description:**
Generate pages at build time and revalidate on a schedule. Best for content that changes infrequently.

**When to Use:**
- Blog posts, documentation, marketing pages
- Data that updates every few minutes to hours
- Pages that must load fast with no server cost per request

**Implementation:**
```typescript
// app/posts/[slug]/page.tsx (App Router)
export async function generateStaticParams() {
  const posts = await fetchAllPosts();
  return posts.map(p => ({ slug: p.slug }));
}

export const revalidate = 3600; // ISR: revalidate every hour

export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await fetchPost(params.slug);
  return <Article post={post} />;
}
```

**Benefits:**
- Zero server cost per request after build
- CDN-cacheable — extremely fast globally
- ISR keeps content fresh without full rebuilds

**Trade-offs:**
- Build time grows with page count
- Stale data window between revalidations

---

### Pattern 2: Server Components + Streaming

**Description:**
Use React Server Components for data-fetching and stream the UI to the browser progressively.

**Implementation:**
```typescript
// Parallel data fetching in Server Component
async function DashboardPage() {
  // These run in parallel on the server
  const [user, metrics] = await Promise.all([
    fetchUser(),
    fetchMetrics(),
  ]);

  return (
    <div>
      <UserHeader user={user} />
      <Suspense fallback={<MetricsSkeleton />}>
        <MetricsPanel metrics={metrics} />
      </Suspense>
    </div>
  );
}
```

**Benefits:**
- Data fetching happens on the server (no client waterfall)
- Streaming improves Time to First Byte (TTFB)
- Zero JS bundle for server-only components

**Trade-offs:**
- Cannot use hooks or browser APIs in Server Components
- Mental model shift from traditional React

---

## Performance Optimization

### Image Optimization
Always use `next/image` — it handles WebP conversion, lazy loading, and layout shift prevention automatically:

```typescript
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // above-the-fold images only
/>
```

### Font Optimization
Use `next/font` to self-host fonts and eliminate FOUT:

```typescript
import { Inter, Playfair_Display } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-display' });
```

### Script Loading Strategy
```typescript
import Script from 'next/script';

// Analytics — load after page is interactive
<Script src="https://analytics.example.com/js" strategy="lazyOnload" />
```

---

## Guidelines

### Code Organization
- `app/` for App Router pages and layouts
- `components/` for shared UI (split into `ui/` primitives and `features/` composites)
- `lib/` for utilities and API clients
- `types/` for shared TypeScript interfaces

### Performance Considerations
- Use `next build && next analyze` to inspect bundle composition
- Set `ANALYZE=true` with `@next/bundle-analyzer`
- Target: LCP < 2.5s, CLS < 0.1, FID < 100ms
- Avoid large third-party scripts in the critical path

### Security Best Practices
- Set security headers in `next.config.js`:
  ```javascript
  const securityHeaders = [
    { key: 'X-Frame-Options', value: 'DENY' },
    { key: 'X-Content-Type-Options', value: 'nosniff' },
    { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
  ];
  ```
- Use middleware for auth checks instead of client-side redirects
- Validate all route params server-side before DB queries

---

## Common Patterns

### Pattern A: Parallel Route Segments
Show multiple pages simultaneously (modals, sidebars) using `@slot` conventions in the App Router.

### Pattern B: Route Handlers as API Layer
```typescript
// app/api/generate/route.ts
export async function POST(req: Request) {
  const body = await req.json();
  // validate with zod
  const stream = await generateStream(body);
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  });
}
```

### Pattern C: Middleware for Edge Auth
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');
  if (!token) return NextResponse.redirect(new URL('/login', request.url));
  return NextResponse.next();
}

export const config = { matcher: '/dashboard/:path*' };
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Fetching Data in Client Components Unnecessarily
Move fetches to Server Components or Route Handlers to reduce client bundle size and avoid waterfalls.

### Anti-Pattern 2: Large `_app.js` / Root Layout
Keep the root layout minimal. Move heavy providers (analytics, feature flags) into sub-layouts or use lazy initialization.

---

## Tools and Resources

### Recommended Tools
- **@next/bundle-analyzer**: Visualize bundle composition
- **Lighthouse CI**: Automate Core Web Vitals checks in CI
- **next-sitemap**: Auto-generate sitemaps for SEO

### Further Reading
- [Next.js Docs](https://nextjs.org/docs)
- [Vercel Speed Insights](https://vercel.com/docs/speed-insights)
- [web.dev Measure](https://web.dev/measure/)

## Conclusion

Next.js optimizations compound. Start with SSG/ISR for cacheable pages, migrate data-heavy pages to Server Components, and use Suspense streaming for progressive loading. Profile with Lighthouse before and after each optimization to validate impact.
