---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-PM-HP200-B"
source_id: "AM-DOC-1078"
title: "ALPHA-HP-200 Hydraulic Press - Preventive Maintenance Procedure"
equipment: "ALPHA-HP-200"
equipment_also_covers: ""
document_type: "maintenance-procedure"
document_type_name: "Preventive maintenance procedure"
revision: "Rev B"
effective_date: "2025-07-01"
status: "current"
supersedes: "ALPHA-PM-HP200-A"
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-MAN-HP200-B, ALPHA-SAF-HP200-LOTO-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-HP-200 Hydraulic Press - Preventive Maintenance Procedure

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-PM-HP200-B |
| Source identifier | AM-DOC-1078 |
| Equipment | ALPHA-HP-200 |
| Document type | Preventive maintenance procedure |
| Revision | Rev B |
| Effective date | 2025-07-01 |
| Status | current |
| Supersedes | ALPHA-PM-HP200-A |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-MAN-HP200-B, ALPHA-SAF-HP200-LOTO-1 |
| Document owner | Maintenance Engineering |

## Purpose

This procedure defines the preventive maintenance tasks for the ALPHA-HP-200
hydraulic press and its power unit ALPHA-P-100: what is done, at what
interval, with what acceptance criterion, and what to do when a criterion is
not met.

Rev B was issued after the 2025 structural survey and the reliability review.
Every interval is shorter than or equal to the interval it replaces, two tasks
have been added to the weekly task, and hose damage is now a replacement
trigger regardless of the age of the hose.

The pressure limits, speeds and torques referenced here are those of the
current controlled revision of the press manual. Where this procedure and the
press manual disagree, the press manual governs and the disagreement is raised
as a documentation defect.

## Interval summary

| Task | Interval | Performed by |
| --- | --- | --- |
| Operator pre-use checks | Every shift | Operator |
| Visual leak and cleanliness check | Daily | Operator |
| Die area and ram wiper cleanliness check | Daily | Operator |
| Grease the four gib blocks and the ram guide shoes | Weekly | Technician |
| Hydraulic hose glance check, full length | Monthly | Technician |
| Reservoir oil level and condition check | Weekly | Technician |
| Safety relay and two-hand control functional test | Monthly | Technician |
| Hydraulic oil analysis, sample point SP-1 | Every 300 running hours, and after any hose burst | Maintenance Engineering |
| Die height sensor calibration | Every 750 running hours | Technician |
| Oil filter element change, return line | Every 2000 running hours | Technician |
| Oil cooler and tank breather clean | Every 2000 running hours | Technician |
| Ram parallelism check | Every 1000 running hours | Maintenance Engineering |
| Hydraulic hose detailed inspection | Every 2000 running hours | Technician |
| Hydraulic hose replacement | On any chafing, bulging or cover damage, at any age | Technician |
| Tie-rod re-torque | Every 2000 running hours | Technician, two person |
| Safety valve pop test | Every 2000 running hours | Maintenance Engineering |
| Post weld visual inspection | Every 3000 running hours | Maintenance Engineering |
| Accelerator alarm function test | Every 3000 running hours | Maintenance Engineering |

Running hours are read from the hour meter at the pendant.

## Safety prerequisites

1. The weekly, 750 hour, 1000 hour and 2000 hour tasks are inside the guard or
inside the die area and may not be started before ALPHA-SAF-HP200-LOTO-1 has been
completed for the specific task, including the green zero-energy verification
tag and the countersignature.

2. 2. The 2000 hour hose inspection and the 2000 hour tie-rod re-torque require the
full zero-energy state and a permit PTW-2600.

3. The oil analysis sample at SP-1 is taken from the pressurised circuit and is
the only task that may be done with the circuit live. It must be done with the
circuit below the maximum working pressure stated in the press manual, with
the nozzle cap fitted on the sample port and the sample taken into an
approved container.

Hose replacement is not permitted with the circuit live under any
circumstances. A hose that has been removed must be capped the same hour.

## Task details and acceptance criteria

### Daily, operator
- Floor and die area clean, no oil pooling. Criterion: dry floor.
- Oil level between the marks on the sight gauge.
- Ram wiper strip clean and complete, no debris rolled under the wiper.
  Criterion: wiper edge visible across the full die face width.
- No visible hose chafing from the operator's position.

### Weekly, technician
- Grease the four gib blocks and the four ram guide shoes with NLGI 2
  lithium complex grease, Alpha specification AM-G2. 6 g per point,
  32 points. Over-greasing is a defect: a grease seal that is over-pressured
  will push grease past the wiper and onto the floor.
- Check reservoir breather and oil colour. Criterion: breather clean, oil
  clear amber. Dark or milky oil is a stop condition, raise a work order for
  an oil analysis outside the interval.
- Check the two-hand control buttons for mechanical damage. Criterion: buttons
  move freely, no gap above 3 mm.

### Monthly, technician
- Hydraulic hose glance check along the full length of every hose using a
  mirror. Acceptance: no chafing, no contact with a moving part, no bulging.
  A failed glance check triggers an immediate replacement, not a detailed
  inspection.
- Safety relay diagnostics: check the two-hand control, the stop function and
  the ram stop switches in the test menu. Criterion: no faults recorded, stop
  time within the limit in the press manual.
- Check the emergency stop mushroom at the pendant. Criterion: latches, resets
  only with the key switch, releases the press for production.

### Every 300 running hours, Maintenance Engineering
- Draw an oil sample at SP-1 and send it for analysis. Acceptance:
  - Viscosity within the viscosity grade stated in the press manual, that is
    plus or minus 10 percent of the nominal value.
  - Water content 0.05 percent by volume or less.
  - Particle count ISO 4406 20/18/16 or cleaner.
  - No metal additive depletion.
  Result: record the report number on the work order. A failed result
  triggers a filter change and a repeat sample regardless of interval.
- An oil sample is also drawn after any hose burst, at any age, before the
  press is returned to production.

### Every 750 running hours, technician
- Die height sensor calibration against the mechanical indicator on the ram.
  Acceptance: indication within 2 mm at the mid point and within 3 mm at both
  ends of the travel.

### Every 1000 running hours
- Ram parallelism check. Acceptance: 0.5 mm maximum per metre of die face.
  Out of tolerance means the gib blocks are adjusted by Maintenance
  Engineering, not by the technician.

### Every 2000 running hours
- Change the return line filter element AM-FL-10. Acceptance: element clean on
  the outlet side, no bypass indication on the filter clogging switch.
- Oil cooler and breather clean. Acceptance: no debris, cooler fins clear.
- Hydraulic hose detailed inspection. As the monthly glance check, plus
  measurement of hose outer diameter at three points on every hose. Acceptance:
  no reduction of more than 1 mm against nominal, no change of shape, no
  softening of the cover.
- Tie-rod re-torque, 340 N.m, torque wrench calibrated and in date, two person
  task, three passes in the diagonal cross pattern from the press manual.
  Acceptance: 340 N.m achieved or the nut turns freely. A nut that turns
  freely is an escalation, not a pass.
- Safety valve pop test with a calibrated test gauge. Acceptance: the valve
  lifts between the set point and the hard-wired trip in the press manual.

### Every 3000 running hours, Maintenance Engineering
- Post weld visual inspection of the four post welds, both fillet welds on
  each post, using a mirror and a bright light. Acceptance: no linear
  indication, no undercut, no crack. Any indication stops the press and
  requires a competent person's structural assessment before return to
  service.
- Accelerator alarm function test. Acceptance: test hammer or simulated
  impact produces an alarm and the alarm is logged.

## Hose replacement rule

A hydraulic hose on this press is replaced when any of the following is
present, at any age and regardless of the hour meter:

- Chafing, abrasion or a flat spot on the outer cover.
- Bulging between the reinforcement layers, even if the outer cover looks
  intact.
- Any cut, nick or split in the outer cover.
- Weeping at a fitting, a crimp or a bend radius.
- Age above 6 years, or above 4 years if the hose has been in a high-heat
  area near the oil cooler.

Record the hose crimp date on the hose tag. Crimped hoses without a tag are
treated as over age.

## Stop-work criteria

Stop the task and escalate to Maintenance Engineering when any of these is
found, irrespective of the interval:

- Any hose with chafing, bulging, a soft spot or oil weeping at a fitting.
- Any tie-rod nut that turns freely, or a tie-rod with movement at the nut.
- A crack in a bolster, a clamp screw or the frame.
- A linear indication on any post weld.
- Oil that is dark, milky, or smells burnt.
- Any reading of the accumulator gauge above 5 bar after the bleed in
  ALPHA-SAF-HP200-LOTO-1.

## Documentation gaps

This procedure does not specify:

- The grease quantity for the HP-200B variant ram guide shoes. Use the
  quantity in AM-PM-HP200 when the asset plate carries the suffix B.
- Torque values for manifold fittings, which are on the fitting vendor data
  sheets.
- Acceptance limits for the condition monitoring accelerometer, which are set
  in the condition monitoring configuration.
- The replacement interval for the counterbalance cylinder seals; this is not
  a preventive item, it is a failure-driven item, and there is no
  manufacturer interval available in this document set.

## Appendix: Revised interval ladder and task mapping

Revision B shortens seven intervals and adds four tasks, as listed in the
interval summary above. The table maps the affected tasks so that a technician
working from a Revision A work order can see what has changed.

| Task | Revision A interval | Revision B interval | Change |
| --- | --- | --- | --- |
| Oil analysis | 500 h | 300 h | Shortened |
| Return filter change | 2000 h | 2000 h | Unchanged |
| Tie-rod re-torque | 4000 h | 2000 h | Shortened |
| Ram drift check | 1000 h | 1000 h | Unchanged |
| Relief valve overhaul | 4000 h | 4000 h | Unchanged |
| Accumulator pre-charge check | 2000 h | 2000 h | Unchanged |
| Safety proof test | Annual | Annual | Unchanged |

The shortened oil analysis interval follows two oil degradation events on the
press in the year before the revision. Shortening the interval without also
addressing the cause only moves the sample earlier; the cause investigation is
recorded in the reliability log and is reviewed at each annual service.

A work order raised under Revision A with the old intervals may be worked, but
the next work order for the same asset must use the Revision B intervals. The
change is recorded in the maintenance management system at the revision
effective date.

## Appendix: Verification and documentation requirements

Every preventive maintenance visit ends with a verification pass and a
documentation check. The verification confirms that the press is safe to
return to production and that the records are complete.

Verification pass, in order:

1. Confirm all guards and interlocks are refitted and function correctly.
2. Confirm the emergency stop stops the ram and latches.
3. Confirm the pressure gauge reads zero with the pump stopped.
4. Confirm no oil is leaking from any joint disturbed during the work.
5. Confirm the oil level is correct and the filter indicators are clear.
6. Run the press through ten cycles at working speed and confirm normal
   operation and no unusual noise.
7. Confirm the work area is clear of tools and the press is tagged back to
   production.

Documentation check:

- The work order records each task, the measured value and the evidence.
- The oil sample report is attached.
- Any part replaced is recorded with its part number and serial number.
- Any deviation from the procedure is recorded with the approving engineer.
- The zero-energy verification record is complete and signed by both people.

The press is not returned to production until both passes are complete.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2023-04-15 | First controlled issue after the press rebuild. |
| Rev B | 2025-07-01 | Structural survey and reliability review. Oil analysis, filter, hose, tie-rod, parallelism and safety valve intervals shortened. Added monthly hose glance check, age based hose replacement and post weld inspection. |
