---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-MAN-OC5T-A"
source_id: "BM-DOC-2275"
title: "BETA-OC-5T Overhead Travelling Crane - Equipment Manual"
equipment: "BETA-OC-5T"
equipment_also_covers: "BETA-OC-5TS and BETA-OC-5TL (variant differences listed under Variant coverage)"
document_type: "equipment-manual"
document_type_name: "Equipment manual"
revision: "Rev A"
effective_date: "2022-12-05"
status: "superseded"
supersedes: ""
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BETA-SAF-OC5T-INS-1, BETA-WO-RULES-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-OC-5T Overhead Travelling Crane - Equipment Manual

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-MAN-OC5T-A |
| Source identifier | BM-DOC-2275 |
| Equipment | BETA-OC-5T |
| Also covers | BETA-OC-5TS and BETA-OC-5TL (variant differences listed under Variant coverage) |
| Document type | Equipment manual |
| Revision | Rev A |
| Effective date | 2022-12-05 |
| Status | superseded |
| Applies to | Assets listed under equipment |
| Related documents | BETA-SAF-OC5T-INS-1, BETA-WO-RULES-1 |
| Document owner | Maintenance Engineering |

## Purpose

This manual describes the BETA-OC-5T single girder overhead travelling
crane, 5.0 tons safe working load at 59 ft span, serving Line 1 at Harbor
Works.

It is the reference used when building a work order for lifting and for the
maintenance of this crane. The manual does not cover slings and shackles; those
are in the lifting equipment register and the lifting plan.

This manual does not cover:

- BETA-OC-5TS, the short travel variant, 5.0 tons, travel limited to plus and
  minus 5 ft, fitted with rail clamps BM-CL-25.
- BETA-OC-5TL, the long travel variant, 5.0 tons, full line travel.
- The 10 ton crane BETA-OC-10T on Line 4.

## Equipment overview

Single girder crane, underhung hook block, two-fall reeving, two trolley
drives and one hoist drive. Power supply is a conductor bar system along the
runway beam.

The hoist gearbox has two brakes, spring applied and hydraulically released,
one on the motor shaft and one on the drum. The hoist is fail-safe: on loss of
power both brakes apply.

The crane is controlled by radio pendant only. There are no pendant sockets
along the runway. The radio pendant has an enable button, a large emergency
stop, and five movement buttons.

The runway consists of two rails on corbels with end stops, wheel buffers and
a runway limit switch at each end.

## Technical data

| Parameter | Value |
| --- | --- |
| Safe working load | 5.0 tons at 59 ft span |
| Maximum hook height | 12 ft 0 in |
| Hoist speed, raising | 8 m/min equivalent, 26 ft/min |
| Hoist speed, lowering | 26 ft/min |
| Trolley speed | 60 ft/min |
| Rope | 3/8 in 6x19 IWRC, grade 1770 N/mm2 |
| Rope discard criterion | 8 broken wires within 10 rope diameters |
| Maximum vertical deflection at mid span under rated load | 30 mm |
| Brake holding torque requirement | 150 percent of rated torque |
| Brake test load, annual | 125 percent of safe working load |
| Proving period | 12 months |
| Hoist limit switch | upper only, at 12 ft 0 in |
| Runway limit switches | one per end of travel |
| Control | radio pendant, no pendant sockets |
| Power supply | 480 V three phase, 7.5 kW hoist, 2 x 1.5 kW travel |

Safe working load is reduced to 4.0 tons when the load is picked up with the
hook more than 8 in off the vertical through the centre of gravity.

## Rated use and limits

1. Rated for indoor use between 40 degF and 104 degF.
2. No lift over a person. No person may be under a suspended load at any time,
   including during a test. The area under the trolley is barricaded before any
   load is raised.
3. Duty cycle: 16 hours per day at 60 percent duty.
4. Slack rope, side pull and a pull more than 15 degrees off vertical are
   prohibited.
5. The rope must not be used partly unwound from the drum; the minimum number
   of wraps on the drum is 4.
6. Loads must not be suspended and left unattended unless the crane is at a
   designated parking position and the load is on a floor-standing support.
7. The radio pendant must be tested before use each shift. A pendant that does
   not pass the self test is removed from service.

## Brake system

- Holding brake on the motor shaft, spring applied, hydraulically released.
- Second brake on the drum, spring applied, released by the same circuit.
- Both brakes must release together. Partial release is a stop condition.
- Brake setting is a maintenance task. The shim figures and the release air
  gap are on the brake data sheet, which is not reproduced here and is not part
  of this document collection.
- A brake that slips under load is not a fault to be monitored. The crane is
  taken out of service and the load is lowered under control.

## Inspection and testing requirements

- Daily operator pre-use inspection: see BETA-SAF-OC5T-INS-1.
- Weekly radio pendant self test and no-load functional test of hoist, travel
  and all limits with the hook empty.
- Monthly documented inspection of ropes, hook, hook latch, limits, brakes and
  the electrical enclosure.
- Annual thorough examination by a competent person, and a brake test at 125
  percent of safe working load with calibrated test weights.
- Annual magnetic particle inspection of the hook and the hook nut.

Every examination and test is recorded in the lifting equipment register for
this crane. The register is not part of this manual.

## Variant coverage

| Parameter | BETA-OC-5T | BETA-OC-5TS short travel | BETA-OC-5TL long travel |
| --- | --- | --- | --- |
| Safe working load | 5.0 tons | 5.0 tons | 5.0 tons |
| Travel range | full line | plus and minus 5 ft | full line plus buffer |
| Rail clamps | BM-CG-18 | BM-CL-25 | BM-CG-18L |
| Travel speed | 60 ft/min | 20 ft/min | 72 ft/min |
| Buffer | wheel buffer, 1 per end | hydraulic buffer, 1 per end | wheel buffer with rubber pad |
| Discard criterion | as Technical data | as Technical data | as Technical data |

The short travel crane has no documented travel limit adjustment procedure in
this document collection. Raise a documentation request before adjusting any
limit on an OC-5TS.

The asset plate on the trolley carries the suffix S or L.

## Documentation gaps

Not contained in this manual:

- The brake shim figures and the release air gap, which are on the brake data
  sheet.
- The rope drum grooving data and the rope replacement procedure,
  BM-PM-OC5T-ROPE, which is not in this collection.
- The wire rope certificate requirements.
- The radio pendant frequency plan and the site radio channel allocation.
- The load test weight calibration certificates, which are in the lifting
  equipment register.
- The upper hoist limit adjustment procedure, BM-PM-OC5T-LIMIT.

## Escalation conditions

Stop using the crane and escalate to Maintenance Engineering and EHS when:

- Any brake slips, or the load lowers without command.
- Any wire rope defect, broken wire, birdcaging, kinks or corrosion.
- The hook, hook nut or hook latch is deformed, worn or cracked.
- A limit switch fails to operate, or operates at the wrong point.
- The radio pendant self test fails.
- Vertical deflection under a static test load exceeds the limit in Technical data.
- A required figure is not in the controlled document set.

For a suspected structural failure of the hoist, lower the load to the floor
if it is safe to do so. If it is not safe, barricade the area and call EHS on
call.

## Appendix: Load test and brake performance records

The BETA-OC-5T crane is load tested before first use and after any change to
the structure, the hoist or the brake. The test is witnessed and recorded. The
record set is retained for the life of the crane.

| Test | Test load | Acceptance criterion | Interval |
| --- | --- | --- | --- |
| Static proof load | 13750 lb, 125 percent | No permanent deformation, no cracking | Before first use and after structural work |
| Dynamic load test | 12100 lb, 110 percent | Smooth operation, brakes hold | Before first use and after hoist work |
| Brake holding test | 11000 lb rated | Holds without drift for 10 minutes | Every 12 months |
| Overload device test | 11550 lb, 105 percent | Prevents hoist above the setting | Every 12 months |
| Limit switch test | Approaching the upper limit | Stops the hoist and allows lowering | Every 3 months |

The static proof load is applied with the crane stationary and the load
suspended clear of the floor. The load is held for ten minutes and the
structure is inspected for cracking at the welds.

No crane is returned to service after a structural repair until a fresh proof
load has been applied and recorded.

## Appendix: Wire rope and hook inspection criteria

The wire rope and hook are the components most likely to cause a dropped
load. They are inspected at the intervals in the main schedule and at every
load test. The criteria below are absolute.

| Item | Rejection criterion | Action |
| --- | --- | --- |
| Broken wires in one lay | 10 or more in a length of 30 times the diameter | Replace the rope |
| Broken wires in one strand | 5 or more in one strand in one lay | Replace the rope |
| Rope diameter reduction | More than 5 percent of nominal | Replace the rope |
| Corrosion | Severe pitting or internal corrosion | Replace the rope |
| Crushing or kinking | Any kink, birdcage or crush | Replace the rope |
| End termination | Crack, slippage or corrosion at the socket | Replace the termination |
| Hook opening | More than 10 percent of the original opening | Replace the hook |
| Hook wear | More than 10 percent of the throat section | Replace the hook |
| Hook twist | More than 10 degrees from the plane | Replace the hook |
| Hook cracks | Any crack in the body or the saddle | Replace the hook |

A rope that fails any criterion is removed from service and the failure is
recorded. The replacement is inspected and its certificate filed before use.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2022-12-05 | First controlled issue after the radio control retrofit on Line 1. |
