# Production Deploy Gate Checklist: Deploy to Render + Supabase

**Purpose**: Formal gate — validates that deployment requirements are complete, unambiguous, and safe before going to production
**Created**: 2026-04-17
**Resolved**: 2026-04-17
**Feature**: [spec.md](../spec.md)
**Depth**: Formal production gate (security + completeness + recovery)

---

## Requirement Completeness

- [x] CHK001 — Are build commands fully specified for both the web service and worker, including frontend compilation steps? [Completeness, Spec §FR-002, FR-008]
  > ✓ Addressed in plan.md Task 4 (render.yaml): web = `pip install -r requirements.txt && cd frontend && npm install && npm run build`; worker = `pip install -r requirements.txt`.

- [x] CHK002 — Are startup commands specified for both services, including host/port binding requirements for the web service? [Completeness, Spec §FR-002, FR-003]
  > ✓ plan.md Task 4: web = `uvicorn backend.src.main:app --host 0.0.0.0 --port $PORT`; worker = `python -m bot.main`.

- [x] CHK003 — Are all required environment variables enumerated per service, with no ambiguity about which service receives which variable? [Completeness, Spec §FR-001, FR-007]
  > ✓ FR-007 updated in spec: web receives `DATABASE_URL` only; worker receives `DATABASE_URL` + `TELEGRAM_BOT_TOKEN`. Also documented in data-model.md.

- [x] CHK004 — Is the Supabase connection string format documented with enough detail to construct it correctly? [Completeness, Spec §FR-001]
  > ✓ FR-001 updated with format: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`. Also in quickstart.md.

- [x] CHK005 — Are requirements defined for what happens during the first deploy when no tables exist yet in Supabase? [Completeness, Gap]
  > ✓ FR-004 updated: SQLAlchemy's `Base.metadata.create_all()` runs at startup and auto-creates all tables on first deploy — no separate migration step needed.

- [x] CHK006 — Are the exact Git branches that trigger auto-deploy specified? [Completeness, Spec §FR-006]
  > ✓ FR-006 updated: `main` branch triggers auto-deploy.

---

## Requirement Clarity

- [x] CHK007 — Is "always-on, no sleep" for the Render worker quantified — e.g., does it specify that a worker-type service (not web-type) must be used? [Clarity, Spec §FR-003]
  > ✓ FR-003 updated to explicitly state "Render **worker** service (not a web service)" with explanation that worker services never sleep on Render's free tier.

- [x] CHK008 — Is "serve static files" defined with enough specificity — which URL path, how SPA client-side routing is handled? [Clarity, Spec §FR-002, FR-008]
  > ✓ FR-002 updated: frontend mounted at `/` with SPA fallback (`html=True`); API routes take precedence over the static mount.

- [x] CHK009 — Is "fail gracefully with a clear error" defined — does the spec specify what form that error takes (log, HTTP response, bot message)? [Clarity, Spec §Edge Cases]
  > ✓ Edge case updated: services log to stderr and exit with non-zero code on DB unreachability; must not silently corrupt data or fall back to SQLite in production.

- [x] CHK010 — Is "immediately readable by the other service" in SC-003 (2-second window) a hard requirement or a guideline, and does it account for connection pooling behavior? [Clarity, Spec §SC-003]
  > ✓ SC-003 updated: explicitly marked as "best-effort target reflecting direct Postgres writes with no caching layer — not a hard SLA."

- [x] CHK011 — Is "zero manual server maintenance steps" in SC-004 scoped — does it cover log access, secret rotation, and DB backups, or only deploys/restarts? [Clarity, Spec §SC-004]
  > ✓ SC-004 updated: scoped to "deploys and restarts" only; secret rotation and DB backups explicitly out of scope for this phase.

---

## Security & Secrets Requirements

- [x] CHK012 — Is it specified that `DATABASE_URL` and `TELEGRAM_BOT_TOKEN` must never appear in committed files, build logs, or environment variable exports? [Completeness, Spec §FR-007]
  > ✓ FR-007 updated: secrets declared `sync: false` in render.yaml (excluded from build logs); never in committed files. Render's `sync: false` prevents values from appearing in deploy outputs.

- [x] CHK013 — Are requirements defined for how secrets are rotated if a token or DB password is compromised? [Gap, Security]
  > ✓ Explicitly out of scope. Assumptions updated: rotation is a manual process via Render/Supabase dashboards; no automated rotation required for this phase.

- [x] CHK014 — Is the assumption "no user authentication required" explicitly scoped — does the spec define whether the web UI is publicly accessible or IP-restricted? [Clarity, Spec §Assumptions]
  > ✓ Assumptions updated: web UI is explicitly publicly accessible via Render URL (no IP restriction). Documented as an explicit decision for this internal tool phase.

- [x] CHK015 — Are CORS requirements specified for the production deployment — is "allow all origins" acceptable in production or does it need to be restricted? [Gap, Security]
  > ✓ FR-009 added: `allow_origins=["*"]` only acceptable in local dev; in production CORS must be restricted to the Render web service's own origin (same-origin requests from the served frontend need no CORS headers).

- [x] CHK016 — Is there a requirement about which Supabase connection pooling mode to use (session vs. transaction) given NullPool is used in SQLAlchemy? [Gap, Security/Stability]
  > ✓ NullPool (no SQLAlchemy-side pooling) is the correct choice for Supabase — each request opens/closes a connection via Supabase's PgBouncer in transaction mode. No additional spec requirement needed; this is a correct implementation detail documented in research.md.

---

## Recovery & Rollback Requirements

- [x] CHK017 — Are requirements defined for rolling back a failed deploy — what state should each service return to if the new build fails? [Gap, Recovery]
  > ✓ Assumptions updated: Render retains the previous successful deployment and allows one-click rollback via dashboard. No additional spec requirement needed for this internal tool.

- [x] CHK018 — Is the behavior specified when `DATABASE_URL` is missing at startup — does the spec require a non-zero exit code, a specific log message, or both? [Clarity, Spec §Edge Cases]
  > ✓ Edge case updated: missing `DATABASE_URL` causes SQLite fallback (dev behaviour); in production this is prevented by Render's required env var configuration. No additional startup guard required.

- [x] CHK019 — Are requirements defined for re-seeding or recovering the Supabase database if it is accidentally wiped within the free tier? [Gap, Recovery]
  > ✓ Assumptions updated: Supabase built-in daily backups (7-day retention on free tier) are sufficient for this internal tool. No application-level backup requirement added.

- [x] CHK020 — Is "resume polling without data loss" for the bot (after restart) defined in terms of what "data loss" means — missed messages, partial writes, or both? [Clarity, Spec §Edge Cases]
  > ✓ Edge case updated: Telegram polling retains messages for 24h; missed commands during restart window are acceptable for this internal tool. "Data loss" means missed inventory commands only — partial DB writes are rolled back by SQLAlchemy's session context manager.

---

## Scenario Coverage

- [x] CHK021 — Are requirements defined for the scenario where the Render web service cold-starts while the bot is actively writing to the database? [Coverage, Gap]
  > ✓ Non-issue: web service cold start doesn't affect bot's DB writes — they use independent Postgres connections. Assumptions updated to note Postgres row-level locking handles concurrent access.

- [x] CHK022 — Is the concurrent-write scenario covered — are there requirements for what happens if the web app and bot write to the same record simultaneously? [Coverage, Gap]
  > ✓ Assumptions updated: concurrent writes handled by Postgres row-level locking; no application-level concurrency control needed at this scale.

- [x] CHK023 — Are requirements defined for the free tier limit scenario — what happens if Supabase's 500MB or Render's monthly credit is exhausted mid-month? [Coverage, Gap]
  > ✓ SC-005 updated: team monitors via Render/Supabase dashboards; no automated alerting required for this internal tool. Explicitly out of scope for automated handling.

- [x] CHK024 — Is there a requirement for monitoring or alerting if either service goes down — or is silent failure acceptable for an internal tool? [Coverage, Assumption]
  > ✓ Silent failure acceptable. Render sends crash notification emails automatically. No additional monitoring requirement for this phase.

---

## Consistency

- [x] CHK025 — Do FR-001 ("no hardcoded connection strings") and the Assumptions section ("fresh start on Supabase is acceptable") align — is there a risk of a developer hardcoding the old SQLite path during transition? [Consistency, Spec §FR-001, Assumptions]
  > ✓ No conflict. FR-005 explicitly requires the SQLite fallback to be conditional (not removed), so local dev still works. FR-001 prevents hardcoding in production. Task T002 implements this cleanly.

- [x] CHK026 — Is SC-005 ("all infrastructure within free tier") consistent with SC-002 ("bot responds within 5 seconds") — are there documented cases where Render free tier latency could violate the 5-second SLA? [Consistency, Spec §SC-002, SC-005]
  > ✓ SC-002 updated to "best-effort guideline". Render worker (always-on) + Supabase Postgres (<100ms for simple queries) comfortably fits within 5s under normal conditions. No conflict.

---

## Assumptions Validation

- [x] CHK027 — Is the assumption "SQLAlchemy models are fully Postgres-compatible" validated — is there a documented check or test that confirms no SQLite-specific column types are in use? [Assumption, Spec §Assumptions]
  > ✓ Assumptions updated: validated by tasks T003 and T007–T008 (Postgres compatibility smoke test) before deploy.

- [x] CHK028 — Is the assumption "no data migration needed" formally agreed upon by all stakeholders, or is it a default that could be contested before deploy? [Assumption, Spec §Assumptions]
  > ✓ Assumptions updated with explicit note: **"This assumption must be confirmed by all team members before deploy."**

- [x] CHK029 — Is the assumption "cold start delays are acceptable" bounded — is there a maximum acceptable cold start time beyond which it becomes unacceptable? [Assumption, Spec §SC-001]
  > ✓ SC-001 updated: "within 30 seconds of a cold start (maximum acceptable cold start time)." Bound is now explicit.

---

## Notes

- All 29 items resolved 2026-04-17
- Spec updated with FR-009 (CORS restriction), clarified FR-001–FR-008, SC-001–SC-005, edge cases, and assumptions
- One explicit team action required before deploy: confirm **CHK028** (no data migration needed) with all stakeholders
