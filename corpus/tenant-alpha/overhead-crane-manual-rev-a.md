---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-MAN-OC5T-A"
source_id: "AM-DOC-1120"
title: "ALPHA-OC-5T Overhead Travelling Crane - Equipment Manual"
equipment: "ALPHA-OC-5T"
equipment_also_covers: "ALPHA-OC-5TS and ALPHA-OC-5TL (variant differences listed under Variant coverage)"
document_type: "equipment-manual"
document_type_name: "Equipment manual"
revision: "Rev A"
effective_date: "2022-11-01"
status: "superseded"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-SAF-OC5T-INS-1, ALPHA-WO-RULES-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-OC-5T Overhead Travelling Crane - Equipment Manual

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-MAN-OC5T-A |
| Source identifier | AM-DOC-1120 |
| Equipment | ALPHA-OC-5T |
| Also covers | ALPHA-OC-5TS and ALPHA-OC-5TL (variant differences listed under Variant coverage) |
| Document type | Equipment manual |
| Revision | Rev A |
| Effective date | 2022-11-01 |
| Status | superseded |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-SAF-OC5T-INS-1, ALPHA-WO-RULES-1 |
| Document owner | Maintenance Engineering |

## Purpose

This manual describes the ALPHA-OC-5T single girder overhead travelling
crane, 5.0 tonnes safe working load at 14.6 m span, installed in Bay 2 and
Bay 5 of Ridgeway Works.

It is the reference used when building a work order for lifting and for the
maintenance of this crane. The manual does not cover the lifting accessories,
the slings and the shackles; those are covered by the lifting equipment
register and the lifting plan.

This manual does not cover:

- ALPHA-OC-5TS, the short travel variant, 5.0 tonnes, travel limited to plus
  and minus 1.5 m, fitted with rail clamps CL-25. See Variant coverage.
- ALPHA-OC-5TL, the long travel variant, 5.0 tonnes, full bay travel.
- The 10 tonne crane ALPHA-OC-10T on the north bay.

## Equipment overview

Single girder box crane, underhung hook, two-fall rope reeving, two
independent trolley drives for long travel, one hoist drive. Power supply is a
festoon cable track on the runway beam.

The hoist gearbox has two brakes: a holding brake on the motor shaft and a
second brake on the drum, both spring applied and hydraulically released. The
hoist is fail-safe: on loss of power both brakes apply and the load is held.

Travel and hoist are controlled from a pendant that plugs into three
take-away sockets along the runway. Each socket has its own enable and
emergency stop.

The runway consists of two rails on corbels with end stops and a floor-mounted
buffer at each end.

## Technical data

| Parameter | Value |
| --- | --- |
| Safe working load | 5.0 t at 14.6 m span |
| Maximum hook height | 4.2 m |
| Hoist speed, raising | 8 m/min |
| Hoist speed, lowering | 8 m/min |
| Trolley speed | 18 m/min |
| Rope | 10 mm 6x19 IWRC, grade 1570 N/mm2 |
| Rope discard criterion | 8 broken wires within 10 rope diameters |
| Maximum vertical deflection at mid span under rated load | 25 mm |
| Brake holding torque requirement | 150 percent of rated torque |
| Brake test load, annual | 125 percent of safe working load |
| Proving period | 12 months |
| Traverse and hoist limit switches | two per direction of travel |
| Rail clamp | CG-18 adjustable, maintenance adjustable only |
| Pendant control | low voltage, three-phase insulated, catenary or radio |
| Power supply | 400 V three phase, 7.5 kW hoist, 2 x 1.5 kW travel |

Safe working load is reduced to 4.0 t for lifts where the hook is not
vertically above the centre of gravity of the load by more than 200 mm.

## Rated use and limits

1. The crane is rated for indoor use between 5 degC and 40 degC.
2. No lift over a person. No person may be under a suspended load at any time,
   including during a test. The exclusion zone below the load is the whole
   area under the trolley, not only the point below the hook.
3. Duty cycle: the crane is rated for 16 hours per day at 60 percent duty.
   Continuous operation beyond that requires the brake and rope inspection
   intervals to be halved.
4. Slack rope, side pull and a pull at more than 15 degrees off vertical are
   prohibited.
5. The crane must not be used to lift with the rope partly on the drum; the
   minimum rope wraps on the drum is 4.
6. Loads must not be suspended and left unattended unless the crane is at a
   designated parking position and the load is either on a floor-standing
   support or mechanically secured.

## Brake system

- Holding brake on the motor shaft, spring applied, hydraulically released.
- Second brake on the drum, spring applied, released by the same hydraulic
  circuit.
- Both brakes must release together. Partial release is a stop condition: the
  load is not suspended on one brake.
- Brake setting is a maintenance task. Adjustment is by nut on the brake
  lever, with the specified number of shims fitted. The adjustment figure for
  the drum brake is on the brake data sheet and is not reproduced here.
- A brake that slips under load is not a fault to be monitored. The crane is
  taken out of service and the load is lowered to the floor under control.

## Inspection and testing requirements

- Daily operator pre-use inspection: see ALPHA-SAF-OC5T-INS-1.
- Weekly no-load functional test of hoist, travel and all limits, with an
  unloaded hook and hands clear of the mechanism.
- Monthly documented inspection of ropes, hook, hook latch, limit switches,
  brakes and the electrical enclosure.
- Annual thorough examination by a competent person, and a brake test at 125
  percent of safe working load with calibrated test weights.
- Annual magnetic particle inspection of the hook and the lifting beam seat.

Every examination and test is recorded in the lifting equipment register for
this crane. The register is not part of this manual.

## Variant coverage

| Parameter | ALPHA-OC-5T | ALPHA-OC-5TS short travel | ALPHA-OC-5TL long travel |
| --- | --- | --- | --- |
| Safe working load | 5.0 t | 5.0 t | 5.0 t |
| Travel range | full bay | plus and minus 1.5 m | full bay plus buffer |
| Rail clamps | CG-18 | CL-25 | CG-18L |
| Travel speed | 18 m/min | 6 m/min | 22 m/min |
| Buffer | floor mounted, 1 per end | hydraulic buffer, 1 per end | floor mounted with rubber pads |

The travel limit adjustment procedure for ALPHA-OC-5TS uses the hydraulic
buffer and is not the same procedure as the one in ALPHA-SAF-OC5T-INS-1. The
short travel crane has no documented travel limit adjustment procedure in this
document collection. Raise a documentation request before adjusting any limit
on an OC-5TS.

The asset plate on the trolley carries the suffix S or L. If the suffix is not
readable, treat the crane as the standard OC-5T only after the register entry
has been checked, and record that check on the work order.

## Documentation gaps

Not contained in this manual:

- The brake shim figures and the brake air gap for the hoist brakes. They are
  on the brake data sheet, which is not in this document collection.
- The rope drum grooving data and the rope replacement procedure. The
  replacement procedure is AM-PM-OC5T-ROPE, which is not in this collection.
- The wire rope certificate requirements and the discard counter reading
  procedure.
- The radio pendant frequency plan for the site.
- The load test weight calibration certificates. Test weights are calibrated
  assets in their own right and their certificates are in the lifting
  equipment register.

## Escalation conditions

Stop using the crane and escalate to Maintenance Engineering and EHS when:

- Any brake slips, or the load lowers without command.
- Any wire rope defect, broken wire, birdcaging, kinks or corrosion.
- The hook, hook nut or hook latch is deformed, worn or cracked.
- A limit switch fails to operate, or operates at the wrong point.
- Any wire, rope or pendant is damaged.
- Vertical deflection under a static test load exceeds the limit in Technical data.
- A required figure is not in the controlled document set.

For a suspected structural failure of the hoist, lower the load to the floor
if it is safe to do so. If it is not safe, barricade the area and call the EHS
on-call number.

## Appendix: Load test and brake performance records

The ALPHA-OC-5T crane is load tested before first use and after any change to
the structure, the hoist or the brake. The test is witnessed and recorded. The
record set is retained for the life of the crane.

| Test | Test load | Acceptance criterion | Interval |
| --- | --- | --- | --- |
| Static proof load | 6.25 t, 125 percent | No permanent deformation, no cracking | Before first use and after structural work |
| Brake holding test | 5.0 t rated | Holds without drift for 10 minutes | Every 12 months |

The only test load stated in this manual is the static proof load at 125 percent
of safe working load, together with the annual brake test at 125 percent of
safe working load. This revision states no dynamic load test load and no
overload device test load, so neither test is performed under this document. A
test that applies a different load requires a controlled test procedure that
states that load before the test is carried out.
| Limit switch test | Approaching the upper limit | Stops the hoist and allows lowering | Every 3 months |

The static proof load is applied with the crane stationary and the load
suspended clear of the floor. The load is held for ten minutes and the
structure is inspected for cracking at the welds. The test is repeated only
after the defect is corrected and re-verified.

No crane is returned to service after a structural repair until a fresh proof
load has been applied and recorded.

## Appendix: Wire rope and hook inspection criteria

The wire rope and hook are the components most likely to cause a dropped
load. They are inspected at the intervals in the main schedule and at every
load test. The criteria below are absolute; there is no discretion to extend
the life of a rope that fails them.

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
recorded. The replacement rope is inspected and its certificate filed with the
crane record before the crane is used.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2022-11-01 | First controlled issue after the crane replacement in Bay 5. |
