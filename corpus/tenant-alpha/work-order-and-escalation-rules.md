---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-WO-RULES-1"
source_id: "AM-DOC-1180"
title: "Field Maintenance Work Order, Documentation and Escalation Rules"
equipment: "all Alpha Manufacturing assets"
equipment_also_covers: ""
document_type: "work-order-rules"
document_type_name: "Work order and escalation rules"
revision: "Rev 1"
effective_date: "2025-09-01"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-MAN-HP200-B, ALPHA-SAF-HP200-LOTO-1, ALPHA-TS-HP200-1"
document_owner: "Maintenance Engineering and Production Support"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# Field Maintenance Work Order, Documentation and Escalation Rules

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-WO-RULES-1 |
| Source identifier | AM-DOC-1180 |
| Equipment | all Alpha Manufacturing assets |
| Document type | Work order and escalation rules |
| Revision | Rev 1 |
| Effective date | 2025-09-01 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-MAN-HP200-B, ALPHA-SAF-HP200-LOTO-1, ALPHA-TS-HP200-1 |
| Document owner | Maintenance Engineering and Production Support |

## Purpose

This document defines how a field symptom is turned into a safe, traceable
work order at Ridgeway Works. It applies to every maintenance technician and
to every asset in Building 2.

It defines the order of the seven steps, the fields a work order must carry,
and the rules for refusing to improvise when the documentation set does not
contain the answer.

## The seven steps, in order

### Step 1: capture the symptom

Record the symptom in the words of the person who reported it. Record the time
it started, the asset, the production condition at the time, the tool or work
piece in the machine, and the ambient and process conditions if the symptom is
temperature or pressure related.

Do not paraphrase. "Hydraulic pressure is unstable" and "the pressure drops
when the ram is down" are different reports and lead to different diagnostic
paths.

### Step 2: identify the equipment

Read the asset plate. Record the full asset identifier, including any suffix,
and the bay. The suffix is part of the identity: HP-200 and HP-200B are not the
same press, OC-5T and OC-5TS are not the same crane.

If the asset plate is unreadable, or the asset is not in the asset register,
stop at step 2. Raise a documentation request. Do not select a document by
guessing the asset.

### Step 3: select the controlled document revision

Every controlled document has a revision and an effective date. Select the
revision with these rules, in this order:

1. Use only the controlled revision. A printed copy on a desk or a photo on a
  phone is not a controlled revision.
2. If the document register lists more than one revision, use the one whose
  effective date is the latest date that is not later than the date of the
  symptom.
3. If the date of the symptom is not known, use the latest effective revision
  and record the assumption in the work order.
4. If the symptom is known to predate the latest revision, use the revision
   that was in force at the time, and flag the work order for engineering
   review, because the equipment may have been changed in the meantime.
5. Never merge values from two revisions of the same document. If a value is
   needed and it is not in the revision you have selected, that is an
   "insufficient information" outcome, not a reason to look in the other
   revision.

Rule 5 is the rule most often broken. Two revisions of one document contain
different numbers for the same limit, and the wrong one is either a safety
problem or an unnecessary teardown.

### Step 4: work the diagnostic sequence

Follow the diagnostic sequence in the document selected in step 3. Record every
measurement, including the ones that exclude a cause. Do not skip a step.

If a step is skipped, record the step number, the reason, and the name of the
person who authorised the skip. A diagnostic sequence is a safety instrument,
not a suggestion list.

If the symptom cannot be narrowed by the documented steps to a single cause,
stop. See step 6.

### Step 5: clear the safety prerequisites

Before any step that requires access inside a guard, to a hydraulic circuit, to
a stored energy source, to a moving part or above floor level, the safety
procedure for that asset must be completed and signed. The work order records
the permit number and the tag number.

No safety prerequisite is cleared by a verbal assurance, by a previous shift's
work order, or by the fact that the machine is currently switched off.

### Step 6: decide: sufficient or insufficient information

The work order carries one of two documentation status values.

- Sufficient: the controlled document set contains the procedure needed to
  complete the task, and the selected revision is unambiguous.
- Insufficient information: the controlled document set does not contain the
  procedure, the value, the acceptance criterion or the revision needed to
  complete the task.

When the status is insufficient information, the technician must stop work and
raise a documentation request. The following are explicitly not allowed:

- Substituting a procedure from another asset, another variant, another
  manufacturer or another site.
- Substituting a value from another revision of the same document.
- Converting a value into another unit system and using the converted figure.
  A converted figure is not a documented figure.
- Using a value read from the as-built drawings, a nameplate or a photograph
  when the controlled document set is silent. Nameplate values are recorded on
  the work order as as-built observations, they are not used as limits.
- Replacing the most probable part as a way of testing a hypothesis.

### Step 7: raise or close the work order

A work order is complete when it contains: the symptom as reported; the asset
identifier; the document identifier and revision used in step 3; every
measurement taken and its acceptance criterion; the cause, or the statement
that the cause is not established; the parts fitted with their part numbers;
any torque or set point applied, with the revision it came from; the
verification test that proves the repair; the permit and tag numbers; and both
signatures.

A work order that does not name the revision used is not a valid work order.

## Work order fields

| Field | Content |
| --- | --- |
| Symptom | Verbatim report, plus time and production condition |
| Asset identifier | Full identifier including suffix, and bay |
| Document identifier | Identifier of the document used |
| Revision used | Revision label and effective date, mandatory |
| Documentation status | Sufficient, or insufficient information |
| Measurements | Value, unit and instrument used |
| Cause | Established cause, or not established |
| Parts | Part numbers and quantities |
| Values applied | Set points and torques, with the revision they came from |
| Verification | Test performed and its result |
| Safety record | Permit number and tag number |
| Signatures | Technician and verifier |

## Escalation rules

Escalate to Level 2 Maintenance Engineering, and continue to the Production
Supervisor, when any of the following occurs:

1. The same symptom on the same asset occurs for the third time within 90 days.
2. A safety device, a limit switch or a protective function fails, on any
   machine.
3. A required value is missing from the controlled document set.
4. Two controlled documents give different values for the same limit and the
   correct value cannot be determined from revision and effective date.
5. An as-built condition differs from the controlled document, for example a
   part that has been modified without a document change.
6. The work requires a structural assessment, a refrigerant intervention or
   work on a pressure vessel.
7. A near miss or an incident occurred, whatever the apparent outcome.

Escalate to EHS in addition, and stop the work, when:

8. Any stored energy was released onto a person, or a person was under a
   suspended load.
9. Any guard or safety circuit was defeated, bypassed or missing.
10. Any work was performed without a completed permit and a verified
    zero-energy state.

Escalation is recorded on the work order with the time, the person notified and
the outcome. Verbal escalation is not escalation.

## Records and retention

- Work orders are retained for the life of the asset plus seven years.
- Certificates for calibrated instruments are retained with the work order
  that used them.
- The lifting equipment register entries are retained by EHS, not on the work
  order, but the work order records the register entry number.
- Electronic records are the record. A work order closed without the
  measurements in Work order fields is not closed, it is abandoned and is reopened.

## Documentation gaps

Not contained in this document:

- The escalation telephone numbers and the out of hours rota.
- The asset register itself.
- The controlled document register.
- The permit issuing authority for each permit series.

## Appendix: Work order reference data

Every work order is raised with the fields below. A field left empty is not an
acceptable work order; the system rejects it until the field is completed.

| Field | Format | Example | Required |
| --- | --- | --- | --- |
| Work order number | WO-YYYY-NNNN | WO-2025-0417 | yes |
| Asset tag | tenant asset identifier | ALPHA-HP-200 | yes |
| Priority | P1 to P4 | P2 | yes |
| Documentation status | sufficient or insufficient information | insufficient information | yes |
| Requested by | role, not a person | Production | yes |
| Permit required | permit type or none | PTW-2600 | yes |
| Isolation required | yes or no | yes | yes |
| Parts required | part number and quantity | RV-200-A, 1 | yes |
| Technical value used | value and the document it came from | 210 bar, ALPHA-MAN-HP200-B | yes |

Priority definitions:

- P1: a safety function is defeated or a person is at risk. Work stops until
  the function is restored or the asset is isolated.
- P2: production is stopped and no safe workaround exists.
- P3: production is degraded, or a redundant asset has failed and the duty has
  been taken by the standby.
- P4: planned work that can be scheduled inside the next maintenance window.

A work order that cites a value not present in the controlled document set is
not closed with a guessed value. It is closed with documentation status
insufficient information and referred to Maintenance Engineering.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2025-09-01 | First controlled issue. |
