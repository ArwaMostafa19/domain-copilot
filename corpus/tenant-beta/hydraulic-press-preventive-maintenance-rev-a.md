---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-PM-HP200-A"
source_id: "BM-DOC-2238"
title: "BETA-HP-200 Hydraulic Press - Preventive Maintenance Procedure"
equipment: "BETA-HP-200"
equipment_also_covers: ""
document_type: "maintenance-procedure"
document_type_name: "Preventive maintenance procedure"
revision: "Rev A"
effective_date: "2023-02-10"
status: "superseded"
supersedes: ""
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BETA-MAN-HP200-A, BETA-SAF-HP200-ECP-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-HP-200 Hydraulic Press - Preventive Maintenance Procedure

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-PM-HP200-A |
| Source identifier | BM-DOC-2238 |
| Equipment | BETA-HP-200 |
| Document type | Preventive maintenance procedure |
| Revision | Rev A |
| Effective date | 2023-02-10 |
| Status | superseded |
| Applies to | Assets listed under equipment |
| Related documents | BETA-MAN-HP200-A, BETA-SAF-HP200-ECP-1 |
| Document owner | Maintenance Engineering |

## Purpose

This procedure defines the preventive maintenance tasks for the
BETA-HP-200 hydraulic press and its power unit P-100: what is done, at what
interval, with what acceptance criterion, and what to do when a criterion is
not met.

The pressure limits, speeds and torques referenced here are those of the
current controlled revision of the press manual. Where this procedure and the
press manual disagree, the press manual governs and the disagreement is raised
as a documentation defect.

## Interval summary

| Task | Interval | Performed by |
| --- | --- | --- |
| Operator pre-use checks | Every shift | Operator |
| Visual leak and cleanliness check | Daily | Operator |
| Grease the ram guides and the gib blocks | Weekly | Technician |
| Reservoir oil level and condition check | Weekly | Technician |
| Safety relay and light curtain function test | Monthly | Technician |
| Hydraulic oil analysis, sample point SP-2 | Every 1000 running hours | Maintenance Engineering |
| Die height sensor calibration | Every 4000 running hours | Technician |
| Pressure gauge calibration | Every 4000 running hours | Technician |
| Return filter element change | Every 4000 running hours | Technician |
| Oil cooler and breather clean | Every 2000 running hours | Technician |
| Ram parallelism check | Every 2000 running hours | Maintenance Engineering |
| Hydraulic hose visual inspection | Every 2000 running hours | Technician |
| Tie-rod re-torque | Every 3000 running hours | Technician, two person |
| Safety valve pop test | Every 4000 running hours | Maintenance Engineering |
| Frame weld visual inspection | Every 6000 running hours | Maintenance Engineering |

Running hours are read from the hour meter at the operator station.

## Safety prerequisites

1. The weekly, 1000 hour, 2000 hour and 4000 hour tasks are inside the guard or
inside the die area and may not be started before BETA-SAF-HP200-ECP-1 has been
completed for the specific task, including the red verification tag and both
signatures.

2. The 2000 hour hose inspection and the 3000 hour tie-rod re-torque require the
full zero-energy state, the cushion block and a permit LOTO-4410.

3. The oil analysis sample at SP-2 is the only task that may be done with the
circuit live, and only below the maximum working pressure in the press manual,
with the nozzle cap fitted and the sample taken into an approved container.

## Task details and acceptance criteria

### Daily, operator
- Floor and die area clean, no oil pooling. Criterion: dry floor.
- Oil level between the marks on the sight glass.
- Light curtain columns and emitters clean, no obstruction in the field.
- No visible hose chafing from the operator's position.

### Weekly, technician
- Grease the two ram guides and the four gib blocks with NLGI 2 lithium
  complex grease, Beta specification BG-2. 0.25 oz per point, 24 points.
  Criterion: grease visible at the seal lip, no hardened residue.
- Check the reservoir breather and oil colour. Criterion: breather clean, oil
  clear amber. Dark or milky oil is a stop condition, not a top-up condition.
- Check that the cushion release valve RV-330 returns to its normal position
  and is hand tight plus one eighth of a turn.

### Monthly, technician
- Safety relay diagnostics: light curtain, stop function, ram limits and
  anti-two-block. Criterion: no faults recorded, stop time within the limit in
  the press manual.
- Check the emergency stop mushroom at the operator station. Criterion:
  latches, resets only with the key switch.
- Function test the light curtain by breaking the field with the test rod at
  three heights. Criterion: ram stops at each height and the diagnostic records
  the stop time.

### Every 1000 running hours, Maintenance Engineering
- Draw an oil sample at SP-2 and send it for analysis. Acceptance:
  - Viscosity within plus or minus 10 percent of the grade in the press
    manual.
  - Water content 0.03 percent by volume or less.
  - Particle count ISO 4406 20/18/16 or cleaner.
  - No metal additive depletion.
  Result: record the report number on the work order. A failed result triggers
  a filter change and a repeat sample regardless of interval.

### Every 2000 running hours
- Oil cooler and breather clean. Acceptance: no debris, cooler fins clear.
- Ram parallelism check. Acceptance: 0.008 in maximum per 12 in of die face.
  Out of tolerance is adjusted by Maintenance Engineering, not by the
  technician.
- Hydraulic hose visual inspection along the full length of every hose, with a
  mirror. Acceptance: no chafing, no bulging, no softening, no weeping at a
  fitting, no contact with a moving part.

### Every 3000 running hours
- Tie-rod re-torque, 2200 lbf.ft, wrench calibrated and in date, two person
  task. Acceptance: 2200 lbf.ft achieved, or the nut turns freely. A nut that
  turns freely is an escalation, not a pass.

### Every 4000 running hours
- Die height sensor calibration against the mechanical indicator. Acceptance:
  indication within 0.08 in at the mid point and within 0.12 in at both ends of
  the travel.
- Pressure gauge calibration against a calibrated reference gauge. Acceptance:
  all three gauges agree within 2 percent of full scale.
- Return filter element change. Acceptance: element clean on the outlet side,
  no bypass indication.
- Safety valve pop test with a calibrated reference gauge. Acceptance: full
  lift between the set point and the hard-wired trip in the press manual.

### Every 6000 running hours, Maintenance Engineering
- Frame weld visual inspection of the frame and the bolster welds, using a
  mirror and a bright light. Acceptance: no linear indication, no undercut, no
  crack.

## Stop-work criteria

Stop the task and escalate to Maintenance Engineering when any of these is
found, irrespective of the interval:

- Any hose with chafing, bulging, a soft spot or oil weeping at a fitting.
- Any tie-rod nut that turns freely, or movement at the nut.
- A crack in a bolster, a clamp, a clamp screw or the frame.
- A linear indication on any weld.
- Oil that is dark, milky or smells burnt.
- Clamp pressure below the minimum in the press manual.
- Any reading of the accumulator gauge above 10 psi after the bleed in
  BETA-SAF-HP200-ECP-1.

## Documentation gaps

This procedure does not specify:

- The grease quantity for the HP-200S straight-side variant guide points.
  Those are on work instruction WI-2204, which is not part of this document
  collection.
- Torque values for manifold and tube fittings, which are on the fitting vendor
  data sheets.
- The die cushion recharge acceptance pressure, which is on commissioning
  sheet CM-HP200-01.

## Appendix: Preventive maintenance task library

The tasks below are the detailed work items behind the interval summary. Each
task states the action, the acceptance criterion and the evidence required.

| Frequency | Task | Acceptance criterion | Evidence |
| --- | --- | --- | --- |
| 4000 h | Change the return filter element | New element, no bypass indicator | Filter part number |
| 1000 h | Sample hydraulic oil | Within ISO 4406 20/18/16 | Laboratory report number |
| 1000 h | Clean the suction strainer | No debris, element undamaged | Photograph |
| 1000 h | Check ram drift with the pump stopped | Less than 0.04 in in 5 minutes | Measured value |
| 3000 h | Re-torque the tie-rod nuts | 2200 lbf.ft, witness marks aligned | Torque certificate |
| 2000 h | Replace the accumulator bladder | Pre-charge 72 psi | Pre-charge pressure |
| 4000 h | Overhaul the main relief valve | Lifts at 2000 psi, reseats below | Bench record |
| 4000 h | Flush the hydraulic circuit | Cleanliness within specification | Particle count |
| Annual | Prove the high-pressure trip | Trips at the set point | Calibrated gauge reading |
| Annual | Prove the two-hand control | Hold time, both channels open | Test record |
| Annual | Calibrate the pressure transducer | Within 1 percent of full scale | Certificate |

A task that cannot be completed to its acceptance criterion is reported to
Maintenance Engineering with the measured value and the suspected cause.

## Appendix: Oil condition monitoring and limits

Hydraulic oil condition is the best single indicator of the health of the
power unit. The oil is sampled from the return line sampling point while the
press is at working temperature.

| Parameter | Limit | Action if exceeded |
| --- | --- | --- |
| Particle count (ISO 4406) | 20/18/16 or cleaner | Change oil and filter, find the ingress path |
| Water content | 200 ppm maximum | Change oil, inspect the breather |
| Viscosity at 104 degF | 46 cSt, plus or minus 10 percent | Change oil |
| Acid number | 0.5 mg KOH/g maximum | Change oil |
| Oxidation | Within the laboratory advisory | Change oil and investigate heat load |
| Copper | 20 ppm maximum | Inspect for bearing or cooler wear |
| Iron | 50 ppm maximum | Inspect pump and valves for wear |

Results are compared against the previous three samples for the same unit, not
against the table alone. A trend rising toward a limit is reported even when
the current value is within limit.

An oil change is recorded with the volume added, the product used and the
running hours at the change.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2023-02-10 | First controlled issue after the Line 1 rebuild. |
