# Production Deploy Gate Checklist: Deploy to Render + Supabase

**Purpose**: Formal gate — validates that deployment requirements are complete, unambiguous, and safe before going to production
**Created**: 2026-04-17
**Feature**: [spec.md](../spec.md)
**Depth**: Formal production gate (security + completeness + recovery)

---

## Requirement Completeness

- [ ] CHK001 — Are build commands fully specified for both the web service and worker, including frontend compilation steps? [Completeness, Spec §FR-002, FR-008]
- [ ] CHK002 — Are startup commands specified for both services, including host/port binding requirements for the web service? [Completeness, Spec §FR-002, FR-003]
- [ ] CHK003 — Are all required environment variables enumerated per service, with no ambiguity about which service receives which variable? [Completeness, Spec §FR-001, FR-007]
- [ ] CHK004 — Is the Supabase connection string format documented with enough detail to construct it correctly? [Completeness, Spec §FR-001]
- [ ] CHK005 — Are requirements defined for what happens during the first deploy when no tables exist yet in Supabase? [Completeness, Gap]
- [ ] CHK006 — Are the exact Git branches that trigger auto-deploy specified? [Completeness, Spec §FR-006]

---

## Requirement Clarity

- [ ] CHK007 — Is "always-on, no sleep" for the Render worker quantified — e.g., does it specify that a worker-type service (not web-type) must be used? [Clarity, Spec §FR-003]
- [ ] CHK008 — Is "serve static files" defined with enough specificity — which URL path, how SPA client-side routing is handled? [Clarity, Spec §FR-002, FR-008]
- [ ] CHK009 — Is "fail gracefully with a clear error" defined — does the spec specify what form that error takes (log, HTTP response, bot message)? [Clarity, Spec §Edge Cases]
- [ ] CHK010 — Is "immediately readable by the other service" in SC-003 (2-second window) a hard requirement or a guideline, and does it account for connection pooling behavior? [Clarity, Spec §SC-003]
- [ ] CHK011 — Is "zero manual server maintenance steps" in SC-004 scoped — does it cover log access, secret rotation, and DB backups, or only deploys/restarts? [Clarity, Spec §SC-004]

---

## Security & Secrets Requirements

- [ ] CHK012 — Is it specified that `DATABASE_URL` and `TELEGRAM_BOT_TOKEN` must never appear in committed files, build logs, or environment variable exports? [Completeness, Spec §FR-007]
- [ ] CHK013 — Are requirements defined for how secrets are rotated if a token or DB password is compromised? [Gap, Security]
- [ ] CHK014 — Is the assumption "no user authentication required" explicitly scoped — does the spec define whether the web UI is publicly accessible or IP-restricted? [Clarity, Spec §Assumptions]
- [ ] CHK015 — Are CORS requirements specified for the production deployment — is "allow all origins" acceptable in production or does it need to be restricted? [Gap, Security]
- [ ] CHK016 — Is there a requirement about which Supabase connection pooling mode to use (session vs. transaction) given NullPool is used in SQLAlchemy? [Gap, Security/Stability]

---

## Recovery & Rollback Requirements

- [ ] CHK017 — Are requirements defined for rolling back a failed deploy — what state should each service return to if the new build fails? [Gap, Recovery]
- [ ] CHK018 — Is the behavior specified when `DATABASE_URL` is missing at startup — does the spec require a non-zero exit code, a specific log message, or both? [Clarity, Spec §Edge Cases]
- [ ] CHK019 — Are requirements defined for re-seeding or recovering the Supabase database if it is accidentally wiped within the free tier? [Gap, Recovery]
- [ ] CHK020 — Is "resume polling without data loss" for the bot (after restart) defined in terms of what "data loss" means — missed messages, partial writes, or both? [Clarity, Spec §Edge Cases]

---

## Scenario Coverage

- [ ] CHK021 — Are requirements defined for the scenario where the Render web service cold-starts while the bot is actively writing to the database? [Coverage, Gap]
- [ ] CHK022 — Is the concurrent-write scenario covered — are there requirements for what happens if the web app and bot write to the same record simultaneously? [Coverage, Gap]
- [ ] CHK023 — Are requirements defined for the free tier limit scenario — what happens if Supabase's 500MB or Render's monthly credit is exhausted mid-month? [Coverage, Gap]
- [ ] CHK024 — Is there a requirement for monitoring or alerting if either service goes down — or is silent failure acceptable for an internal tool? [Coverage, Assumption]

---

## Consistency

- [ ] CHK025 — Do FR-001 ("no hardcoded connection strings") and the Assumptions section ("fresh start on Supabase is acceptable") align — is there a risk of a developer hardcoding the old SQLite path during transition? [Consistency, Spec §FR-001, Assumptions]
- [ ] CHK026 — Is SC-005 ("all infrastructure within free tier") consistent with SC-002 ("bot responds within 5 seconds") — are there documented cases where Render free tier latency could violate the 5-second SLA? [Consistency, Spec §SC-002, SC-005]

---

## Assumptions Validation

- [ ] CHK027 — Is the assumption "SQLAlchemy models are fully Postgres-compatible" validated — is there a documented check or test that confirms no SQLite-specific column types are in use? [Assumption, Spec §Assumptions]
- [ ] CHK028 — Is the assumption "no data migration needed" formally agreed upon by all stakeholders, or is it a default that could be contested before deploy? [Assumption, Spec §Assumptions]
- [ ] CHK029 — Is the assumption "cold start delays are acceptable" bounded — is there a maximum acceptable cold start time beyond which it becomes unacceptable? [Assumption, Spec §SC-001]

---

## Notes

- Items marked `[Gap]` indicate requirements that are absent from the spec and should be added or explicitly excluded before production deploy
- Items marked `[Assumption]` should be reviewed with the team before sign-off
- Check items off as completed: `[x]`
- Add findings or decisions inline as comments
