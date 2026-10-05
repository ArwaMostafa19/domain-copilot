---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-PM-HP200-A"
source_id: "AM-DOC-1078"
title: "ALPHA-HP-200 Hydraulic Press - Preventive Maintenance Procedure"
equipment: "ALPHA-HP-200"
equipment_also_covers: ""
document_type: "maintenance-procedure"
document_type_name: "Preventive maintenance procedure"
revision: "Rev A"
effective_date: "2023-04-15"
status: "superseded"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-MAN-HP200-A, ALPHA-SAF-HP200-LOTO-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-HP-200 Hydraulic Press - Preventive Maintenance Procedure

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-PM-HP200-A |
| Source identifier | AM-DOC-1078 |
| Equipment | ALPHA-HP-200 |
| Document type | Preventive maintenance procedure |
| Revision | Rev A |
| Effective date | 2023-04-15 |
| Status | superseded |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-MAN-HP200-A, ALPHA-SAF-HP200-LOTO-1 |
| Document owner | Maintenance Engineering |

## Purpose

This procedure defines the preventive maintenance tasks for the ALPHA-HP-200
hydraulic press and its power unit ALPHA-P-100: what is done, at what
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
| Grease the four gib blocks and the ram guide shoes | Weekly | Technician |
| Reservoir oil level and condition check | Weekly | Technician |
| Safety relay and two-hand control functional test | Monthly | Technician |
| Hydraulic oil analysis, sample point SP-1 | Every 500 running hours | Maintenance Engineering |
| Oil filter element change, return line | Every 2000 running hours | Technician |
| Die height sensor calibration | Every 1000 running hours | Technician |
| Hydraulic hose visual inspection | Every 4000 running hours | Technician |
| Tie-rod re-torque | Every 4000 running hours | Technician, two person |
| Ram parallelism check | Every 2000 running hours | Maintenance Engineering |
| Safety valve pop test | Every 4000 running hours | Maintenance Engineering |
| Post weld visual inspection | Every 6000 running hours | Maintenance Engineering |
| Oil cooler and tank breather clean | Every 2000 running hours | Technician |

Running hours are read from the hour meter at the pendant.

## Safety prerequisites

1. The weekly, 500 hour, 1000 hour and 2000 hour tasks are inside the guard or
inside the die area and may not be started before ALPHA-SAF-HP200-LOTO-1 has been
completed for the specific task, including the green zero-energy verification
tag and the countersignature.

2. The 4000 hour hose inspection and the 4000 hour tie-rod re-torque require the
full zero-energy state and a permit PTW-2600.

3. The oil analysis sample at SP-1 is taken from the pressurised circuit and is
the only task that may be done with the circuit live. It must be done with the
circuit below the maximum working pressure stated in the press manual, with
the nozzle cap fitted on the sample port and the sample taken into an
approved container.

## Task details and acceptance criteria

### Daily, operator
- Floor and die area clean, no oil pooling. Criterion: dry floor.
- Oil level between the marks on the sight gauge.
- No visible hose chafing from the operator's position.

### Weekly, technician
- Grease the four gib blocks and the four ram guide shoes with NLGI 2
  lithium complex grease, Alpha specification AM-G2. 5 g per point, 32 points.
  Criterion: grease visible at the seal lip, no hardened residue, no
  over-pressured grease seal.
- Check reservoir breather and oil colour. Criterion: breather clean, oil
  clear amber. Dark or milky oil is a stop condition, raise a work order for
  an oil analysis outside the interval.
- Check the two-hand control buttons for mechanical damage. Criterion: buttons
  move freely, no gap above 3 mm.

### Monthly, technician
- Safety relay diagnostics: check the two-hand control, the stop function and
  the ram stop switches in the test menu. Criterion: no faults recorded, stop
  time within the limit in the press manual.
- Check the emergency stop mushroom at the pendant. Criterion: latches, resets
  only with the key switch, releases the press for production.

### Every 500 running hours, Maintenance Engineering
- Draw an oil sample at SP-1 and send it for analysis. Acceptance:
  - Viscosity within the viscosity grade stated in the press manual, that is
    plus or minus 10 percent of the nominal value.
  - Water content 0.05 percent by volume or less.
  - Particle count ISO 4406 20/18/16 or cleaner.
  - No metal additive depletion.
  Result: record the report number on the work order. A failed result
  triggers a filter change and a repeat sample regardless of interval.

### Every 1000 running hours, technician
- Die height sensor calibration against the mechanical indicator on the ram.
  Acceptance: indication within 2 mm at the mid point and within 3 mm at both
  ends of the travel.

### Every 2000 running hours
- Change the return line filter element AM-FL-10. Acceptance: element clean on
  the outlet side, no bypass indication on the filter clogging switch.
- Oil cooler and breather clean. Acceptance: no debris, cooler fins clear.
- Ram parallelism check. Acceptance: 0.5 mm maximum per metre of die face.
  Out of tolerance means the gib blocks are adjusted by Maintenance
  Engineering, not by the technician.

### Every 4000 running hours
- Hydraulic hose visual inspection along the full length of every hose, with a
  mirror where needed. Acceptance: no chafing, no bulging, no softening, no
  weeping at a fitting, no evidence of contact with a moving part.
- Tie-rod re-torque, 340 N.m, torque wrench calibrated and in date, two
  person task with the cross pattern. Acceptance: 340 N.m achieved or the nut
  turns freely. A nut that turns freely is an escalation, not a pass.
- Safety valve pop test with a calibrated test gauge. Acceptance: the valve
  lifts between the set point and the hard-wired trip in the press manual.

## Stop-work criteria

Stop the task and escalate to Maintenance Engineering when any of these is
found, irrespective of the interval:

- Any hose with chafing, bulging, a soft spot or oil weeping at a fitting.
- Any tie-rod nut that turns freely, or a tie-rod with movement at the nut.
- A crack in a bolster, a clamp screw or the frame.
- Oil that is dark, milky, or smells burnt.
- Any reading of the accumulator gauge above 5 bar after the bleed in
  ALPHA-SAF-HP200-LOTO-1.

## Documentation gaps

This procedure does not specify:

- The grease quantity for the HP-200B variant ram guide shoes. They are
  recorded on variant addendum AM-PM-HP200B, which is not part of this document
  collection.
- Torque values for manifold fittings, which are on the fitting vendor data
  sheets.
- Acceptance limits for the condition monitoring accelerometer, which are set
  in the condition monitoring configuration.

## Appendix: Preventive maintenance task library

The tasks below are the detailed work items behind the interval summary. Each
task states the action, the acceptance criterion and the evidence that must be
recorded. A task is complete only when the evidence is on the work order.

| Frequency | Task | Acceptance criterion | Evidence |
| --- | --- | --- | --- |
| 2000 h | Change the return filter element | New element, no bypass indicator | Filter part number |
| 500 h | Sample hydraulic oil | Within ISO 4406 20/18/16 | Laboratory report number |
| 1000 h | Clean the suction strainer | No debris, element undamaged | Photograph |
| 1000 h | Check the ram drift with the pump stopped | Less than 1 mm in 5 minutes | Measured value |
| 4000 h | Re-torque the tie-rod nuts | 340 N.m, witness marks aligned | Torque wrench certificate |
| 2000 h | Replace the accumulator bladder | Pre-charge 5 bar | Pre-charge pressure |
| 4000 h | Overhaul the main relief valve | Lifts at 240 bar, reseats below 230 bar | Bench record |
| 4000 h | Flush the hydraulic circuit | Cleanliness within specification | Particle count |
| Annual | Prove the high-pressure trip | Trips at 250 bar | Calibrated gauge reading |
| Annual | Prove the two-hand control | 900 ms hold, both channels open | Test record |
| Annual | Calibrate the pressure transducer | Within 1 percent of full scale | Calibration certificate |

A task that cannot be completed to its acceptance criterion is reported to
Maintenance Engineering with the measured value and the suspected cause before
the press is returned to service.

## Appendix: Oil condition monitoring and limits

Hydraulic oil condition is the single best indicator of the health of the
power unit. The oil is sampled from the sampling point SP-1 on the return line
while the press is at working temperature. The sample is taken with the press
running so that the oil is representative of the circuit.

| Parameter | Limit | Action if exceeded |
| --- | --- | --- |
| Particle count (ISO 4406) | 20/18/16 or cleaner | Change oil and filter, find the ingress path |
| Water content | 200 ppm maximum | Change oil, inspect the breather |
| Viscosity at 40 degC | 46 cSt, plus or minus 10 percent | Change oil |
| Acid number | 0.5 mg KOH/g maximum | Change oil |
| Oxidation | Within the laboratory advisory | Change oil and investigate heat load |
| Copper | 20 ppm maximum | Inspect for bearing or cooler wear |
| Iron | 50 ppm maximum | Inspect pump and valves for wear |

Results are compared against the previous three samples for the same unit, not
against the table alone. A trend that is rising toward a limit is reported even
when the current value is within limit.

An oil change is recorded with the volume added, the product used and the
running hours at the change. The oil is disposed of through the site waste
contractor and the disposal record is filed with the work order.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2023-04-15 | First controlled issue after the press rebuild. |
