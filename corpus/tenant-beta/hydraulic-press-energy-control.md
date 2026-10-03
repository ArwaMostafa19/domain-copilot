---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-SAF-HP200-ECP-1"
source_id: "BM-DOC-2231"
title: "BETA-HP-200 Hydraulic Press - Energy Control Program"
equipment: "BETA-HP-200"
equipment_also_covers: "BETA-HP-200S (additional requirements under Additional requirements for BETA-HP-200S)"
document_type: "safety-procedure"
document_type_name: "Safety / energy isolation procedure"
revision: "Rev 1"
effective_date: "2023-03-01"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BETA-MAN-HP200-B, BETA-PM-HP200-B, BETA-DIA-P100-1"
document_owner: "EHS and Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-HP-200 Hydraulic Press - Energy Control Program

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-SAF-HP200-ECP-1 |
| Source identifier | BM-DOC-2231 |
| Equipment | BETA-HP-200 |
| Also covers | BETA-HP-200S (additional requirements under Additional requirements for BETA-HP-200S) |
| Document type | Safety / energy isolation procedure |
| Revision | Rev 1 |
| Effective date | 2023-03-01 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | BETA-MAN-HP200-B, BETA-PM-HP200-B, BETA-DIA-P100-1 |
| Document owner | EHS and Maintenance Engineering |

## Purpose and scope

This program describes how electrical, hydraulic, die cushion and
gravitational energy are made safe on the BETA-HP-200 press before any person
opens a guard, enters the die area, touches a tie rod, handles a hose or
fitting, or opens the manifold.

It applies to BETA-HP-200 and to BETA-HP-200S.

Rule 1. No person may open a guard, enter the die area or break a hydraulic
line on this press unless this program has been completed for the specific
task and the red verification tag is attached.

Rule 2. On this press a two-person rule applies. The person performing the
work and a second authorised person who watches the energy control steps
must both sign the verification tag. This rule is not a formality: the
die cushion stores energy that is not visible from the operating station.

## Energy sources on this machine

| Energy | Source | Isolation point |
| --- | --- | --- |
| Electrical, 460 V three phase | Feeder BM-MCC-3 | Panel 3B-11, breaker 7 |
| Electrical, control 24 V DC | Control transformer in panel 3B-11 | Breaker 9 |
| Hydraulic, main circuit | Power unit P-100, pumps A and B | Ball valves HX-301 and HX-302 |
| Hydraulic, tool clamp circuit | Clamp manifold | Ball valve HX-311 |
| Stored pressure, accumulator AC-2 | Nitrogen pre-charge, 1000 psi as built | Manual bleed valve BV-321 into drain drum DD-2 |
| Stored pressure, die cushion | Cushion cylinder | Cushion release valve RV-330, then cushion block CB-9 |
| Gravitational | Ram mass, about 900 lb | Ram block RB-6 plus tie-off |
| Pneumatic, control only | Instrument air at 60 psi | Ball valve AV-315 |
| Residual | Disconnected hoses | Cap on removal, blank plug before work |

The die cushion is the difference between this press and the four-post presses
elsewhere on the site. Blocking the ram alone does not make the cushion safe.

## Required sequence

Perform these steps in order. Skipping a step is a reportable event.

1. Notify. Inform the Line 1 shift supervisor and the press operators that the
   press will be down, and record it on permit LOTO-4410.

2. Stop normally. Press stop at the operator station and allow the pumps to run
   down for the full 60 seconds. Do not use the emergency stop as a normal
   stopping method.

3. Isolate electrical energy. Open panel 3B-11, set breaker 7 to OFF and the
   isolator handle to the locked position, and fit a personal lock and tag.
   Isolate the control supply at breaker 9. Use the lock box when more than one
   person is working.

4. Isolate the hydraulic supply. Close HX-301 and HX-302, and lock both. Close
   HX-311 on the clamp circuit and lock it. Close instrument air at AV-315.

5. Dissipate the die cushion energy. Open cushion release valve RV-330 and
   let the cushion extend. Fit the cushion block CB-9 in the ram yoke before
   the ram is moved. The cushion pressure is only released when RV-330 is open
   and the ram yoke has dropped onto CB-9.

6. Dissipate the accumulator energy. Open bleed valve BV-321 and discharge
   accumulator AC-2 into drain drum DD-2. Never vent a charged accumulator to
   atmosphere. Continue bleeding until the accumulator gauge reads 10 psi or
   less. If the gauge will not come below 10 psi, stop and escalate; the
   accumulator or the gauge is defective and the circuit must be treated as
   charged.

7. Fit the ram block and tie-off. Fit ram block RB-6 under the ram yoke and fit
   the tie-off. Both must be fitted before hands enter the die area.

8. Verify the zero-energy state. Perform all five verifications:
   - Attempt start from the operator station: nothing moves.
   - Attempt to operate the locked ball valves: they do not move.
   - Attempt to move the ram by hand at the ram crown: it does not move.
   - Confirm the cushion pressure gauge at the cushion manifold reads 0 psi.
   - Confirm the accumulator gauge reads 10 psi or less and the main pressure
     gauge reads 0 psi.
   Attach the red verification tag. Both the technician and the second
   authorised person sign it.

The attempt start verification is recorded on permit LOTO-4410 and is audited
monthly.

## Rules that are frequently broken

- Working on a hose or fitting because the pump motor is off. Motor off is
  not isolation.
- Blocking the ram without releasing the cushion. The cushion can still drive
  the ram down.
- One person signing the verification tag.
- Assuming the accumulator is empty because it was bled on a previous job.
  The gauge reading on the day, by that person, is the evidence.
- Removing a hose and leaving the port open. Cap the port the same hour.
- Leaving a personal lock off during a break. Every break means re-verification.
- Bypassing the light curtain to run the press in setup mode. Prohibited.

## Return to service

1. Remove tools, blanks and test pieces from the die area. Fit all guards.
2. Close BV-321, remove drain drum DD-2, close RV-330 after confirming the
   cushion is recharged on the next cycle.
3. Remove the cushion block CB-9, the ram block RB-6 and the tie-off and return
   them to the store.
4. Remove locks one at a time; each person removes their own lock.
5. Notify the Line 1 supervisor that the press is released.
6. Restore panel 3B-11 and close HX-301, HX-302, HX-311 and AV-315.
7. Recharge accumulator AC-2 through the charging point. The pre-charge value
   is the as-built value on the data plate. Do not charge from a figure copied
   from another press on this site.
8. Run a dry cycle with the die area empty and hands clear. Confirm the cushion
   recharges, the clamp pressure proves, the ram raises and lowers normally and
   there is no leak.
9. Record the return to service on permit LOTO-4410 and on the work order.

## Additional requirements for BETA-HP-200S

The straight-side variant has a fixed guard and a two-tool clamp arrangement.
Before work on its clamp circuit, both clamp circuits must be isolated and
bled separately, because the two clamp circuits are cross connected upstream
of HX-311.

Work instruction WI-2204 covers the HP-200S and is not part of this document
collection. Where this program and WI-2204 differ, raise a documentation
conflict; do not choose between them in the field.

## Incident reporting

Report to EHS before the next shift, even if nobody was hurt:

- A guard was opened or a fitting loosened while the circuit was charged.
- A person entered the die area with the cushion charged.
- An attempt start produced any movement of the ram.
- A tag was found without a lock, or a lock was found unlocked.
- Work was performed without a two-person verification.
- A safety device was found bypassed, taped or missing.

## Appendix: Energy isolation point schedule

The energy isolation points for the BETA-HP-200 press and its hydraulic power
unit are listed below. Every point is locked and tagged before work begins.
The schedule is verified against the as-built drawing at each annual review.

| Ref | Energy source | Device | Location | Method | Verification |
| --- | --- | --- | --- | --- | --- |
| HV-101 | Electrical, main | Isolator | Panel 1A-02 | Lock open | Test for dead at motor terminals |
| HV-201 | Electrical, control | Isolator | Panel 1A-02 | Lock open | Test control voltage absent |
| HY-1 | Hydraulic, stored | Relief and drain valve | Manifold | Open and drain | Gauge reads zero |
| AC-1 | Pneumatic, accumulator | Block valve BV-103 | Manifold | Open to drain vessel | Accumulator gauge reads zero |
| ME-1 | Mechanical, gravity | Ram block and tie-off | Frame | Fit mechanical stop | Ram cannot move under load |
| TH-1 | Thermal | Oil cooler | Power unit | Allow to cool | Below 104 degF |

Isolation is not complete until every point has been applied and the
zero-energy state has been verified by attempting to start the press and
confirming nothing moves. The attempt is recorded with date, time and name.

Two people are required: the person who applied the isolation and a second
person who confirms the zero-energy state independently.

## Appendix: Permit and record retention

The isolation permit is raised for each job and closed only after the
isolation has been removed and the press returned to service. The permit
identifies the asset, the work order, the isolation points applied, the
verifying person and the time of removal.

Records are retained for seven years. The record set for each job contains:

- the raised permit and the lock and tag numbers issued;
- the zero-energy verification record with the attempted-start result;
- the list of isolation points and how each was proven dead;
- the name of the person who applied the isolation and the verifier;
- the time the isolation was removed and the press returned to service;
- any deviation and the approval that authorized it.

A permit that cannot be produced when requested is treated as an unverified
isolation and the work is stopped until the record is reconstructed and
re-verified.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2023-03-01 | First controlled issue, issued with the energy control program audit. |
