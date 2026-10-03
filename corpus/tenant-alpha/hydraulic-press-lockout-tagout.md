---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-SAF-HP200-LOTO-1"
source_id: "AM-DOC-1071"
title: "ALPHA-HP-200 Hydraulic Press - Energy Isolation and Zero-Energy Verification"
equipment: "ALPHA-HP-200"
equipment_also_covers: "ALPHA-HP-200B"
document_type: "safety-procedure"
document_type_name: "Safety / energy isolation procedure"
revision: "Rev 1"
effective_date: "2023-05-15"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-MAN-HP200-B, ALPHA-PM-HP200-B, ALPHA-DIA-P100-1"
document_owner: "EHS and Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-HP-200 Hydraulic Press - Energy Isolation and Zero-Energy Verification

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-SAF-HP200-LOTO-1 |
| Source identifier | AM-DOC-1071 |
| Equipment | ALPHA-HP-200 |
| Also covers | ALPHA-HP-200B |
| Document type | Safety / energy isolation procedure |
| Revision | Rev 1 |
| Effective date | 2023-05-15 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-MAN-HP200-B, ALPHA-PM-HP200-B, ALPHA-DIA-P100-1 |
| Document owner | EHS and Maintenance Engineering |

## Purpose and scope

This procedure describes how electrical, hydraulic, gravitational and
residual energy are made safe on the ALPHA-HP-200 press and on its power unit
ALPHA-P-100 before any person opens a guard, touches a tie rod, handles a hose
or fitting, opens the manifold, works on the die height sensor or performs any
diagnostic measurement inside the die area.

Applies to ALPHA-HP-200 and ALPHA-HP-200B. It does not apply to ALPHA-HP-210,
which is isolated under AM-SAF-HP210-LOTO-1.

Rule 1. No person may open a guard, break a seal, touch a hydraulic line or
enter the die area of this press unless this procedure has been completed for
that specific task and the green zero-energy verification tag is attached to
the isolation points.

Rule 2. Rule 1 applies even when the press appears switched off. The ram, the
counterbalance cylinders and accumulator AC-1 store energy after the pump
motor stops.

## Energy sources on this machine

| Energy | Source | Isolation point |
| --- | --- | --- |
| Electrical, 400 V three phase | Feeder AM-MCC-3 | Panel 3A-04, breaker 3A-04-01 |
| Electrical, control 24 V DC | Control transformer in panel 3A-04 | Breaker 3A-04-07 |
| Hydraulic, pressurised | Power unit ALPHA-P-100 | Ball valves HV-101 and HV-201 |
| Stored hydraulic pressure | Accumulator AC-1, nitrogen pre-charge | Manual bleed valve BV-103 into drain vessel DV-1 |
| Gravitational | Ram mass, about 1600 kg | Mechanical block plus tie-off on the ram yoke |
| Pneumatic, control only | 6 bar instrument air | Ball valve AV-311 |
| Residual | Pressurised hoses that have been disconnected | Cap after disconnection, blank plug before work |

The press has no pneumatic energy in the press circuit itself. Instrument air
actuates the clamp circuit only.

## Required sequence

Perform these six steps in order. Skipping a step is an incident and must be
reported.

1. Notify. Inform the Bay 2 shift supervisor and the operators of press line
   2 that the press will be out of service, and record the notification in the
   permit PTW-2600.

2. Stop normally. Press the stop button at the pendant, let the pump motor run
   down for the full 40 seconds, then set the controls to neutral. Do not use
   the emergency stop as a normal stopping method; the emergency stop drops
   the ram in an uncontrolled way.

3. Isolate electrical energy. Open panel 3A-04, set breaker 3A-04-01 to OFF
   and the isolator handle to the locked position. Fit your personal lock and
   a tag. Fit the lock box if more than one person works on the press. Verify
   the control supply at breaker 3A-04-07 is also isolated. A padlock on the
   isolator handle is the only accepted electrical isolation for this press.

4. Isolate the hydraulic supply. Close ball valve HV-101 (supply from the
   pump) and ball valve HV-201 (return to tank). Both valves have padlockable
   brackets. Fit locks and tags. Close instrument air at AV-311.

5. Dissipate stored energy. This step is not optional and cannot be delegated.
   - Open manual bleed valve BV-103 and discharge accumulator AC-1 into drain
     vessel DV-1. Never vent a charged accumulator to atmosphere.
   - Watch the accumulator gauge on power unit ALPHA-P-100. Continue bleeding
     until the gauge reads 5 bar or less. If it will not come below 5 bar, stop
     and escalate; the accumulator or the gauge is defective and the circuit
     must be treated as charged.
   - Run the pump motor down in bypass if the pump has not been run down
     naturally, then close HV-101.
   - Fit the mechanical block under the ram yoke and fit the tie-off on the ram
     yoke. The block and the tie-off must both be fitted before hands enter the
     die area.

6. Verify the zero-energy state. Perform all four verifications:
   - Attempt start: try to start the press from the pendant. Nothing must move
     and the pendant must show the lockout state.
   - Attempt to operate the isolation valves: the locked ball valves must not
     move.
   - Attempt to move the ram by hand at the ram crown. It must not move.
   - Confirm the accumulator gauge reads 5 bar or less and the pressure gauge
     at the manifold reads 0 bar.
   Attach the green zero-energy verification tag. The tag is signed by the
   technician and countersigned by a second authorised person who has
   personally witnessed step 6.

A document-controlled attempt start verification is mandatory for this press.
The attempt start record is part of permit PTW-2600 and is audited.

## Rules that are frequently broken

- Working on a hose or fitting because "the pump is off". The pump being off
  is not isolation. HV-101, HV-201 and the accumulator bleed are all required.
- Assuming the accumulator is empty because it was bled last week. The gauge
  reading is the evidence, on the day, for that person.
- Removing a hose and leaving the port open. Cap the port immediately and
  install a blank plug before the next task.
- Using a hoist, a forklift or a vehicle as a test weight or as a hold-down.
- Leaving a personal lock off the isolator when the work stops for a break.
  Every break means re-verification.
- Defeating the two-hand control to speed up a mechanical job. This requires a
  documented risk assessment, a permit and a second authorised person.

## Return to service

1. Remove tools, blanks and test pieces from the die area. Fit all guards and
   fix all fasteners. Check that the tie-off and the mechanical block are
   still serviceable and return them to the store.
2. Close all bleed and drain points that were opened, and remove drain vessel
   DV-1.
3. Remove locks one at a time. Each person removes their own lock. The person
   who applied the isolator supervises the removal.
4. Tell the Bay 2 supervisor that the press is released.
5. Restore panel 3A-04 to ON and close HV-101, HV-201 and AV-311.
6. Recharge accumulator AC-1 through the charging point. The pre-charge value
   is the as-built value on the data plate; do not charge from a figure copied
   from another press.
7. Restore electrical energy and run a dry cycle with the die area empty and
   hands clear of the die area. Confirm the ram raises and lowers normally, the
   pressure reading is steady and no leak is visible.
8. Record the return to service in permit PTW-2600 and on the work order.

If the work involved the tie rods, the bolsters, the ram or the frame, the
post-run checks in AM-PM-HP200 apply before production use.

## Incident reporting

Any of the following is a reportable event and is reported to EHS before the
next shift, even if nobody was hurt:

- A guard was opened or a fitting was loosened while the circuit was charged.
- An attempt start produced any movement of the ram.
- Stored energy was released onto a person, or a person entered the die area
  with the ram loaded.
- A lock was found unlocked, or a tag was found without a lock.
- A person worked on the press without a completed permit PTW-2600.

## Appendix: Energy isolation point schedule

The energy isolation points for the ALPHA-HP-200 press and its hydraulic power
unit are listed below. Every point is locked and tagged with the green
zero-energy tag before work begins. The schedule is verified against the
as-built drawing at each annual review.

| Ref | Energy source | Device | Location | Method | Verification |
| --- | --- | --- | --- | --- | --- |
| HV-101 | Electrical, main | Isolator | Panel 3A-04 | Lock open | Test for dead at motor terminals |
| HV-201 | Electrical, control | Isolator | Panel 3A-04 | Lock open | Test control voltage absent |
| HY-1 | Hydraulic, stored | Relief and drain valve | Manifold | Open and drain | Gauge reads zero at TP-3 |
| AC-1 | Pneumatic, accumulator | Block valve BV-103 | Manifold | Open to drain vessel | Accumulator gauge reads zero |
| ME-1 | Mechanical, gravity | Ram block and tie-off | Frame | Fit mechanical stop | Ram cannot move under load |
| TH-1 | Thermal | Oil cooler | Power unit | Allow to cool | Surface temperature below 40 degC |

Isolation is not complete until every point in the schedule has been applied
and the zero-energy state has been verified by attempting to start the press
and confirming that nothing moves. The verification attempt is recorded with
the date, time and the name of the person who made it.

Two people are required for verification: the person who applied the isolation
and a second person who confirms the zero-energy state independently.

## Appendix: LOTO permit and record retention

The isolation permit PTW-2600 is raised for each job and closed only after
the isolation has been removed and the press has been returned to service. The
permit identifies the asset, the work order, the isolation points applied, the
verifying person and the time of removal.

Records are retained for seven years. The record set for each job contains:

- the raised permit and the lock and tag numbers issued;
- the zero-energy verification record with the attempted-start result;
- the list of isolation points and how each was proven dead;
- the name of the person who applied the isolation and the verifier;
- the time the isolation was removed and the press returned to service;
- any deviation, and the approval that authorized it.

A permit that cannot be produced when requested is treated as an unverified
isolation and the work is stopped until the record is reconstructed and
re-verified.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2023-05-15 | First controlled issue for the four-post press and its power unit. |
