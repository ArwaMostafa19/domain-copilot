---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-SAF-OC5T-INS-1"
source_id: "AM-DOC-1126"
title: "ALPHA-OC-5T Overhead Crane - Inspection Procedure"
equipment: "ALPHA-OC-5T"
equipment_also_covers: "ALPHA-OC-5TL (long travel variant)"
document_type: "inspection-procedure"
document_type_name: "Inspection procedure"
revision: "Rev 1"
effective_date: "2023-09-01"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-MAN-OC5T-B, ALPHA-WO-RULES-1"
document_owner: "EHS and Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-OC-5T Overhead Crane - Inspection Procedure

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-SAF-OC5T-INS-1 |
| Source identifier | AM-DOC-1126 |
| Equipment | ALPHA-OC-5T |
| Also covers | ALPHA-OC-5TL (long travel variant) |
| Document type | Inspection procedure |
| Revision | Rev 1 |
| Effective date | 2023-09-01 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-MAN-OC5T-B, ALPHA-WO-RULES-1 |
| Document owner | EHS and Maintenance Engineering |

## Purpose and legal basis

This procedure covers the inspection and testing of the ALPHA-OC-5T overhead
travelling crane. It defines the pre-use inspection, the routine inspections,
the six monthly tests and the annual thorough examination.

The thorough examination, the proof test and the register entries are
carried out to satisfy the site lifting equipment regulation and are recorded
in the lifting equipment register for this crane. This procedure does not
replace the register.

## Safety rules that apply to every task in this procedure

These rules are not optional and no test overrides them:

1. No person may be under a suspended load at any time, including during
   inspection, testing and brake proving. The area under the trolley is
   barricaded before any load is raised.
2. The pendant user stands clear of the load path and keeps both hands on the
   pendant at all times. The pendant is never left unattended while a load is
   suspended.
3. Test weights only. A vehicle, a forklift, a pallet of steel or a stack of
   stock must never be used as a test load. Test weights for this crane are
   calibrated at 5.0 t and their certificates are in the lifting equipment
   register.
4. The electrical isolation for any work on the trolley, the hoist or the
   rope is: isolator on the crane festoon supply at the wall box WB-CRANE-2,
   locked and tagged, with an attempt start verified from the pendant.
5. A work at height over a public area requires the area to be closed or
   protected by debris netting.
6. Only trained and authorised crane operators may use the crane. Trainees
   work under the supervision of an authorised operator and the pendant is
   held by the authorised operator.

## Pre-use inspection, every shift, operator

Performed with the crane parked, the hook empty and no load suspended.
Approximately 5 minutes.

1. Check the rope, from the drum to the hook block, for broken wires,
   birdcaging, kinks, corrosion and flattened sections.
2. Check the hook for spread, throat opening increase, wear on the inside of
   the hook, and the security of the hook nut.
3. Check that the hook latch closes fully and cannot be opened by hand.
4. Check the end stops and the buffers are intact and in position.
5. Check that the travel and hoist limit switches are undamaged and that the
   pendant cable and plug are undamaged.
6. Check the pendant emergency stop and confirm the pendant is the correct one
   for the socket in use.
7. Check the runway for anything that has been left in the swept path.

Any failed item: do not use the crane, tag the pendant out of service at the
socket, and raise a work order.

## Weekly no-load functional test

Performed by the operator with the hook empty, hands clear of the mechanism.

- Raise the hook to the upper limit and confirm the upper limit switch
  operates.
- Lower the hook to within 200 mm of the lower limit and confirm the lower
  limit switch operates.
- Traverse the full travel in each direction and confirm both travel limit
  switches operate at each end.
- Confirm both brakes apply when power is removed: interrupt the power at the
  pendant plug and observe that the empty hook does not drift.

A hook that drifts after power removal is a stop condition. Lower the hook to
the floor, tag the crane out of service and raise a work order.

## Monthly documented inspection

Performed by a maintenance technician under isolation for the rope and brake
checks.

Rope:
- Clean the rope, run the full length through the drum and over the sheaves,
  and inspect the running surface and the terminations.
- Count broken wires within 10 rope diameters of each other and compare with
  the discard criterion in the current revision of the crane manual.
- Check that rope lubrication is present on the working surfaces. Over-lubrication
  is a defect: oil on the sheave grooves attracts grit.

Hook and hook block:
- Check throat opening against the dimension recorded at commissioning. A
  15 percent increase is the discard point.
- Check for cracks at the shank and the saddle with a magnetic particle
  inspection when the 6 monthly test falls due.
- Check sheave rotation, side clearance and bearing noise.

Brakes:
- With the rope isolated and the load removed, apply the brakes and measure
  the release air gap with a feeler gauge against the brake data sheet. If
  the brake data sheet is not available at the machine, stop and raise a
  documentation request; do not adjust to a figure from memory.

Limits and interlocks:
- Confirm the upper hoist limit, lower hoist limit, travel limits, and the
  anti-two-block contact. Anti-two-block contact must act before the hoist
  reaches the mechanical stop.

Record the inspection in the register.

## Six monthly tests

These tests are performed by a competent person with the load test weights.
The test load, the test interval and the acceptance limits are those of the
current controlled revision of the crane manual, not those of a printed copy.

1. Static proof load test at the test load stated in the current controlled
   revision of the crane manual. Apply the load in one step, hold for
   10 minutes, measure the deflection at mid span and compare it with the
   deflection limit in that same revision.
2. Brake test at the same test load: raise the load to 1 m, stop the hoist and
   confirm that neither brake slips. Measure the brake holding torque.
3. Magnetic particle inspection of the hook and the hook nut.
4. Ultrasonic rope inspection of the hoist rope, performed by the contracted
   inspection service.

If the deflection or the brake test fails, the crane is taken out of service,
the load is lowered under control, and the result is recorded as a failure with
the measured value.

## Annual thorough examination

By a competent person who is not the person who performs the routine
maintenance. The examination covers:

- A full examination of the structure, the gearbox, the brakes, the rope, the
  hook, the limit switches, the pendant, the runway, the rails, the corbels,
  the end stops, the buffers and the electrical supply.
- Functional tests of all safety devices.
- A review of the register entries since the last examination.
- A wire rope discard counter reading, if a counter is fitted.
- A review of the operator pre-use inspection records for missed items.

A defect found at examination that makes the crane unsafe stops the crane
immediately. Findings that do not stop the crane are closed within 10 working
days with the due date recorded in the register.

## Stop criteria

The crane is stopped and barricaded immediately on any of the following:

- Any broken wire cluster meeting the discard criterion in the manual.
- Throat opening increase of 15 percent or more.
- Any crack found by magnetic particle or ultrasonic inspection.
- Brake slip under a test load.
- Deflection above the manual limit under a static test load.
- Limit switch or anti-two-block failure.
- Any structural damage, including a damaged rail, corbel or end stop.
- An undocumented safety device, for example a pendant with a bypassed
  emergency stop.

## Documentation gaps

Not contained in this procedure:

- The rope discard counter reading method, where a counter is fitted.
- The magnetic particle and ultrasonic acceptance criteria, which belong to the
  inspection service specification.
- The brake air gap and shim figures, which are on the brake data sheet.
- The wire rope replacement procedure, AM-PM-OC5T-ROPE, which is not in this
  document collection.
- The proof load factor for the OC-5TS short travel crane, which has a
  hydraulic buffer rather than a floor mounted buffer.

## Appendix: Detailed inspection checklist and intervals

This appendix expands the inspection procedure into a checklist with intervals
and acceptance criteria. The checklist is completed in full at each inspection
and the result of each item is recorded.

| Interval | Item | Acceptance criterion |
| --- | --- | --- |
| Daily | Emergency stop | Stops all motion and latches |
| Daily | Hoist brake | Holds the hook without drift |
| Daily | Limit switches | Stop the hoist in both directions |
| Daily | Pendant | Buttons return, cable undamaged |
| Weekly | Wire rope | No broken wires, no kinks |
| Weekly | Hook | No cracks, opening within limit |
| Weekly | Runway | Clear, rail not worn beyond limit |
| Monthly | End stops | Present and secure |
| Monthly | Wheel flanges | Within wear limit |
| Monthly | Festoon system | Cable not chafed |
| Quarterly | Structural welds | No cracks |
| Quarterly | Bolts and fasteners | Torqued per drawing |
| Annual | Proof load | Per the load test schedule |
| Annual | Electrical insulation | Above the minimum resistance |

Items that are not due at an inspection are marked not due, not left blank. A
blank item is treated as not inspected and the inspection is not complete.

## Appendix: Defect classification and reporting

Defects found during inspection are classified so that the correct action is
taken without delay. Classification is not a judgement about how hard the
defect is to fix; it is about the risk if the crane continues to be used.

Class 1, stop use immediately: any crack in a primary structural member, a
failed brake, a failed limit switch, a failed emergency stop, a hook with
cracks or beyond the wear limit, or a rope that fails a rejection criterion.

Class 2, repair before the next planned lift: worn wheel flanges within limit,
chafed festoon cables, loose fasteners, corrosion with less than 10 percent
section loss, or a limit switch that operates but is slow.

Class 3, monitor at the next inspection: paint damage, light surface rust,
minor oil weeps, or a pendant button that is stiff but works.

A Class 1 defect is reported immediately and the crane is tagged out. A Class
2 defect is raised as a work order and scheduled. A Class 3 defect is recorded
and re-checked at the next inspection. The classification and the action are
recorded together so that the decision can be audited.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2023-09-01 | First controlled issue, aligned with the site lifting equipment regulation. |
