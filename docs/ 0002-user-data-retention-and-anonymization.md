# ADR 0002: User Data Retention, Pseudonymization and Deletion

## Status
Proposed

## Context
ForenLIMS processes personal data of laboratory staff (name, email) and links
this data to forensic work products (reports, samples, analyses). Retention
obligations vary significantly by jurisdiction, document type, and case
escalation status:

- **GenDG**: Minimum 30 years for parentage reports
- **GTfCh guidelines**: Long-term auditability of forensic reports
- **ISO 17025/17020**: Documented responsibility for analytical results
- **Jurisdiction-specific policies**: e.g. Bavarian Interior Ministry guidelines
  orient retention periods on applicable statutes of limitations, with
  non-expiring retention (defined as >99 years) for homicide cases

Retention requirements are not static — a case may be escalated after
the institute's work is complete (e.g. grievous bodily harm escalating
to manslaughter), changing the applicable retention period without the
institute being notified. This is an organizational problem outside the
scope of ForenLIMS.

## Decision

### User lifecycle
Users transition through three states:

1. **Active** — staff member is employed, all data visible and accessible
2. **Inactive/Pseudonymized** — staff member has left the institute;
   personal data is retained internally but suppressed in UI output
   where not legally required; all links to work products are preserved
3. **Deleted** — all linked work products have been deleted after expiry
   of their retention period; user record and associated audit trail
   can be fully removed

Full deletion of a user is only permitted when no linked work products
remain in the system. The system will enforce this constraint.

### Retention policies
Retention periods are configurable per document type and jurisdiction.
A `RetentionPolicy` model (to be designed) will define applicable periods.
The system records the retention policy at the time of document creation.
Subsequent policy changes do not retroactively affect existing records —
a human administrator must manually reclassify if escalation becomes known.

### Deletion and audit trail
- No data is deleted automatically; all deletions require explicit
  administrator confirmation
- When work products are deleted, the audit trail records what was deleted,
  by whom, and when — but not the content of the deleted records
- When a user is fully deleted, their audit trail entries are also removed,
  as they no longer serve a traceable purpose
- A separate, minimal deletion log records that a user existed and was
  deleted, without retaining personal data

## Consequences
- `CustomUser` carries an `anonymized_at` field as audit marker
- Personal fields are formally classified in
  `accounts/tests/test_admin_user.py::TestUserAnonymization`
- `RetentionPolicy` model design is deferred until case and sample
  management modules are in place
- Pseudonymization and deletion logic will be implemented in a
  dedicated compliance pass after core modules are complete

## Open Questions
- Exact data model for `RetentionPolicy` and its relation to case types
- How to handle cases where retention period changes after document creation
- International jurisdiction support beyond German regulatory framework
- Technical design of the deletion log (separate table, append-only, etc.)
