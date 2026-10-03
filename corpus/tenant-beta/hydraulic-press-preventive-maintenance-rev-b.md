---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-PM-HP200-B"
source_id: "BM-DOC-2238"
title: "BETA-HP-200 Hydraulic Press - Preventive Maintenance Procedure"
equipment: "BETA-HP-200"
equipment_also_covers: ""
document_type: "maintenance-procedure"
document_type_name: "Preventive maintenance procedure"
revision: "Rev B"
effective_date: "2025-06-01"
status: "current"
supersedes: "BETA-PM-HP200-A"
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BETA-MAN-HP200-B, BETA-SAF-HP200-ECP-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-HP-200 Hydraulic Press - Preventive Maintenance Procedure

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-PM-HP200-B |
| Source identifier | BM-DOC-2238 |
| Equipment | BETA-HP-200 |
| Document type | Preventive maintenance procedure |
| Revision | Rev B |
| Effective date | 2025-06-01 |
| Status | current |
| Supersedes | BETA-PM-HP200-A |
| Applies to | Assets listed under equipment |
| Related documents | BETA-MAN-HP200-B, BETA-SAF-HP200-ECP-1 |
| Document owner | Maintenance Engineering |

## Purpose

This procedure defines the preventive maintenance tasks for the
BETA-HP-200 hydraulic press and its power unit P-100: what is done, at what
interval, with what acceptance criterion, and what to do when a criterion is
not met.

Rev B was issued after the Q1 2025 incident review. Every interval is shorter
than or equal to the interval it replaces, a monthly hose inspection has been
added, and the number of greasing points and the quantity per point have been
corrected.

## Interval summary

| Task | Interval | Performed by |
| --- | --- | --- |
| Operator pre-use checks | Every shift | Operator |
| Visual leak and cleanliness check | Daily | Operator |
| Light curtain column and emitter clean | Weekly | Operator |
| Grease the ram guides and the gib blocks | Weekly | Technician |
| Reservoir oil level and condition check | Weekly | Technician |
| Hydraulic hose glance check, full length | Monthly | Technician |
| Safety relay and light curtain function test | Monthly | Technician |
| Hydraulic oil analysis, sample point SP-2 | Every 500 running hours, and after any hose failure | Maintenance Engineering |
| Ram parallelism check | Every 1000 running hours | Maintenance Engineering |
| Hydraulic hose detailed inspection | Every 1000 running hours | Technician |
| Oil cooler and breather clean | Every 2000 running hours | Technician |
| Die height sensor calibration | Every 2000 running hours | Technician |
| Pressure gauge calibration | Every 2000 running hours | Technician |
| Return filter element change | Every 2000 running hours | Technician |
| Tie-rod re-torque | Every 1500 running hours | Technician, two person |
| Safety valve pop test | Every 2000 running hours | Maintenance Engineering |
| Frame weld visual inspection | Every 3000 running hours | Maintenance Engineering |

Running hours are read from the hour meter at the operator station.

## Safety prerequisites

The weekly, 1000 hour, 1500 hour and 2000 hour tasks are inside the guard or
inside the die area and may not be started before BETA-SAF-HP200-ECP-1 has been
completed for the specific task, including the red verification tag and both
signatures.

The 1000 hour hose inspection and the 1500 hour tie-rod re-torque require the
full zero-energy state, the cushion block and a permit LOTO-4410.

The oil analysis sample at SP-2 is the only task that may be done with the
circuit live, and only below the maximum working pressure in the press manual,
with the nozzle cap fitted and the sample taken into an approved container.

Hose replacement is not permitted with the circuit live under any
circumstances. A hose that has been removed is capped the same hour.

## Task details and acceptance criteria

### Daily, operator
- Floor and die area clean, no oil pooling. Criterion: dry floor.
- Oil level between the marks on the sight glass.
- Light curtain columns and emitters clean, no obstruction in the field.
- No visible hose chafing from the operator's position.

### Weekly, operator
- Clean the light curtain columns and emitters with a lint free cloth. No
  solvent. A column that cannot be cleaned with a dry cloth is replaced.

### Weekly, technician
- Grease the two ram guides and the four gib blocks with NLGI 2 lithium
  complex grease, Beta specification BG-2. 0.25 oz per point, 24 points.
  Over-greasing is a defect: it pushes grease past the wiper and onto the
  floor.
- Check the reservoir breather and oil colour. Criterion: breather clean, oil
  clear amber.
- Check that the cushion release valve RV-330 returns to its normal position
  and is hand tight plus one eighth of a turn.

### Monthly, technician
- Hydraulic hose glance check along the full length of every hose using a
  mirror. Acceptance: no chafing, no contact with a moving part, no bulging.
  A failed glance check triggers immediate replacement, not a detailed
  inspection.
- Safety relay diagnostics: light curtain, stop function, ram limits and
  anti-two-block. Criterion: no faults recorded, stop time within the limit in
  the press manual.
- Function test the light curtain by breaking the field with the test rod at
  three heights. Criterion: ram stops at each height and the diagnostic records
  the stop time.

### Every 500 running hours, Maintenance Engineering
- Draw an oil sample at SP-2 and send it for analysis. Acceptance:
  - Viscosity within plus or minus 10 percent of the grade in the press
    manual.
  - Water content 0.03 percent by volume or less.
  - Particle count ISO 4406 20/18/16 or cleaner.
  - No metal additive depletion.
  A failed result triggers a filter change and a repeat sample regardless of
  interval.
- An oil sample is also drawn after any hose failure, at any age, before the
  press is returned to production.

### Every 1000 running hours
- Ram parallelism check. Acceptance: 0.008 in maximum per 12 in of die face.
- Hydraulic hose detailed inspection. As the monthly glance check, plus outer
  diameter measurement at three points on every hose. Acceptance: no reduction
  of more than 0.04 in against nominal, no change of shape, no softening of the
  cover.

### Every 1500 running hours
- Tie-rod re-torque, 2200 lbf.ft, wrench calibrated and in date, two person
  task, three passes in the diagonal sequence from the press manual.
  Acceptance: 2200 lbf.ft achieved, or the nut turns freely.

### Every 2000 running hours
- Die height sensor calibration. Acceptance: indication within 0.08 in at the
  mid point and within 0.12 in at both ends of the travel.
- Pressure gauge calibration against a calibrated reference gauge.
  Acceptance: all three gauges agree within 2 percent of full scale.
- Return filter element change. Acceptance: element clean on the outlet side,
  no bypass indication.
- Safety valve pop test with a calibrated reference gauge. Acceptance: full
  lift between the set point and the hard-wired trip in the press manual.
- Oil cooler and breather clean. Acceptance: no debris, cooler fins clear.

### Every 3000 running hours, Maintenance Engineering
- Frame weld visual inspection of the frame and the bolster welds, using a
  mirror and a bright light. Acceptance: no linear indication, no undercut, no
  crack. Any indication stops the press and requires a competent person's
  structural assessment before return to service.

## Hose replacement rule

A hydraulic hose on this press is replaced when any of the following is
present, at any age and regardless of the hour meter:

- Chafing, abrasion or a flat spot on the outer cover.
- Bulging between the reinforcement layers, even if the outer cover looks
  intact.
- Any cut, nick or split in the outer cover.
- Weeping at a fitting, a crimp or a bend radius.
- Age above 8 years, or above 5 years if the hose has been in a high heat area
  near the oil cooler.

Record the crimp date on the hose tag. Crimped hoses without a tag are treated
as over age.

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
- The replacement interval for the tool clamp cylinder seals; this is a
  failure-driven item and there is no manufacturer interval available in this
  document set.

## Appendix: Revised interval ladder and task mapping

Revision B shortens two intervals. The table maps the old schedule to the new
one so that a technician working from a Revision A work order can see what has
changed.

| Task | Revision A interval | Revision B interval | Change |
| --- | --- | --- | --- |
| Oil analysis | 500 h | 300 h | Shortened |
| Return filter change | 500 h | 500 h | Unchanged |
| Tie-rod re-torque | 4000 h | 2000 h | Shortened |
| Ram drift check | 1000 h | 1000 h | Unchanged |
| Relief valve overhaul | 4000 h | 4000 h | Unchanged |
| Accumulator pre-charge check | 2000 h | 2000 h | Unchanged |
| Safety proof test | Annual | Annual | Unchanged |

The shortened oil analysis interval follows two oil degradation events on the
press in the year before the revision. Shortening the interval without
addressing the cause only moves the sample earlier; the cause investigation is
recorded in the reliability log and reviewed at each annual service.

A work order raised under Revision A with the old intervals may be worked, but
the next work order for the same asset must use the Revision B intervals.

## Appendix: Verification and documentation requirements

Every preventive maintenance visit ends with a verification pass and a
documentation check. The verification confirms the press is safe to return to
production and the records are complete.

Verification pass, in order:

1. Confirm all guards and interlocks are refitted and function correctly.
2. Confirm the emergency stop stops the ram and latches.
3. Confirm the pressure gauge reads zero with the pump stopped.
4. Confirm no oil is leaking from any joint disturbed during the work.
5. Confirm the oil level is correct and the filter indicators are clear.
6. Run the press through ten cycles and confirm normal operation.
7. Confirm the work area is clear and the press is tagged back to production.

Documentation check:

- The work order records each task, the measured value and the evidence.
- The oil sample report is attached.
- Any part replaced is recorded with its part number and serial number.
- Any deviation is recorded with the approving engineer.
- The zero-energy verification record is complete and signed by both people.

The press is not returned to production until both passes are complete.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2023-02-10 | First controlled issue after the Line 1 rebuild. |
| Rev B | 2025-06-01 | Q1 2025 incident review. Oil analysis, filter, hose, tie-rod, gauge and parallelism intervals shortened. Added monthly hose glance check, weekly light curtain clean and age based hose replacement. |
