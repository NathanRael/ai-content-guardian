# Plan — AI Content Guardian frontend

## Context
- Stack: Next.js 16 + React 19 + TypeScript strict + Tailwind CSS v4 + shadcn/ui + Recharts.
- Base API URL: `NEXT_PUBLIC_API_URL`.
- Language: French UI, no emoji, light mode only, lucide-react icons.
- Follow `frontend-project-structure`, `component-architecture`, `data-fetching`, `design-system`, `code-standard` skills.

## Steps

1. **Dependencies**
   - [x] Check installed packages.
   - [ ] Add `recharts`.

2. **Shared infrastructure**
   - [ ] Create `types/moderation.ts` with global API response types.
   - [ ] Create `lib/api-client.ts` typed client for all Part 0 endpoints + French error handling.
   - [ ] Create `constants/query-keys.ts` with query keys for React Query.
   - [ ] Create `lib/query-client.ts` (or reuse if exists) — not present, will create minimal provider.
   - [ ] Update `app/layout.tsx` to French `lang`, light mode only, remove dark classes, add `Toaster` + QueryProvider.

3. **Shared UI components** (`components/shared/moderation/`)
   - [ ] `comment-card.tsx`
   - [ ] `confidence-bar.tsx`
   - [ ] `model-comparison-panel.tsx`
   - [ ] `explanation-panel.tsx`
   - [ ] `recommendation-banner.tsx`
   - [ ] `translation-notice.tsx`
   - [ ] `stats-summary.tsx`
   - [ ] `bias-audit-chart.tsx`

4. **Feature hooks** (`features/moderation/hooks/`)
   - [ ] `use-analyze-comment.ts`
   - [ ] `use-generate-comments.ts`
   - [ ] `use-analyze-comments.ts`
   - [ ] `use-get-metrics.ts`
   - [ ] `use-get-bias-audit.ts`
   - [ ] `use-get-model-info.ts`
   - [ ] `use-latest-batch.ts` (cached batch summary + results for dashboard)

5. **Pages**
   - [ ] `app/page.tsx` → redirect to `/tableau-de-bord`.
   - [ ] `app/tableau-de-bord/page.tsx` + wrapper + dashboard content.
   - [ ] `app/analyser/page.tsx`.
   - [ ] `app/simulation/page.tsx`.
   - [ ] `app/audit/page.tsx`.
   - [ ] `app/fiche-modele/page.tsx`.
   - [ ] `app/layout.tsx` navigation/sidebar links.

6. **Documentation**
   - [ ] Read `backend/exigences_obligatoires.md`.
   - [ ] Append frontend evidence section mapping components/pages to requirements.

7. **Verification**
   - [ ] Run `pnpm lint` and fix errors.
   - [ ] Run `pnpm build` and fix errors.

## Progress
- Completed: all steps.
