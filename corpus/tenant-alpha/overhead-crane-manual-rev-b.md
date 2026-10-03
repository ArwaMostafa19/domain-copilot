---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-MAN-OC5T-B"
source_id: "AM-DOC-1120"
title: "ALPHA-OC-5T Overhead Travelling Crane - Equipment Manual"
equipment: "ALPHA-OC-5T"
equipment_also_covers: "ALPHA-OC-5TS and ALPHA-OC-5TL (variant differences listed under Variant coverage)"
document_type: "equipment-manual"
document_type_name: "Equipment manual"
revision: "Rev B"
effective_date: "2025-02-10"
status: "current"
supersedes: "ALPHA-MAN-OC5T-A"
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
| Document identifier | ALPHA-MAN-OC5T-B |
| Source identifier | AM-DOC-1120 |
| Equipment | ALPHA-OC-5T |
| Also covers | ALPHA-OC-5TS and ALPHA-OC-5TL (variant differences listed under Variant coverage) |
| Document type | Equipment manual |
| Revision | Rev B |
| Effective date | 2025-02-10 |
| Status | current |
| Supersedes | ALPHA-MAN-OC5T-A |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-SAF-OC5T-INS-1, ALPHA-WO-RULES-1 |
| Document owner | Maintenance Engineering |

## Purpose

This manual describes the ALPHA-OC-5T single girder overhead travelling
crane, 5.0 tonnes safe working load at 14.6 m span, installed in Bay 2 and
Bay 5 of Ridgeway Works.

It is the reference used when building a work order for lifting and for the
maintenance of this crane.

Rev B was issued after the 2024 wire rope inspection campaign and the review of
hoist brake failures on the site. The engineering changes are: a lower
discard criterion for wire ropes, a lower deflection limit, lower hoist speed
for heavy lifts, and additional non-destructive testing at shorter intervals.

## Reason for this revision

The 2024 campaign found two ropes in the site fleet with wire breakage below
the old discard criterion, and one drum brake that released partially under a
static load. No person was injured in either case. The review concluded that
the previous discard criterion and the previous inspection frequency were not
detecting degradation early enough for a crane used daily on general
maintenance work.

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

## Technical data

| Parameter | Value |
| --- | --- |
| Safe working load | 5.0 t at 14.6 m span |
| Maximum hook height | 4.2 m |
| Hoist speed, raising, loads up to 3.0 t | 8 m/min |
| Hoist speed, raising, loads above 3.0 t | 6 m/min |
| Hoist speed, lowering | 8 m/min |
| Trolley speed | 18 m/min |
| Rope | 10 mm 6x19 IWRC, grade 1570 N/mm2 |
| Rope discard criterion | 6 broken wires within 10 rope diameters |
| Maximum vertical deflection at mid span under rated load | 20 mm |
| Brake holding torque requirement | 150 percent of rated torque |
| Brake test load | 110 percent of safe working load |
| Brake test interval | 6 months |
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
7. For loads above 3.0 t the hoist is used in the reduced speed range in
   Technical data. The speed change is made before the load is lifted, not during
   the lift.
8. A lift that requires the crane to travel with the load suspended above 1 m
   is prohibited.

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
- A partial brake release is now treated as a load-handling incident and is
  reported to EHS, because a load suspended on one brake has no redundancy.

## Inspection and testing requirements

- Daily operator pre-use inspection: see ALPHA-SAF-OC5T-INS-1.
- Weekly no-load functional test of hoist, travel and all limits, with an
  unloaded hook and hands clear of the mechanism.
- Monthly documented inspection of ropes, hook, hook latch, limit switches,
  brakes and the electrical enclosure.
- Ultrasonic rope inspection of the hoist rope: every 6 months.
- Magnetic particle inspection of the hook and the hook nut: every 6 months.
- Annual thorough examination by a competent person.
- Brake test at 110 percent of safe working load with calibrated test
  weights: every 6 months.

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
| Discard criterion | as Technical data | as Technical data | as Technical data |

The travel limit adjustment procedure for ALPHA-OC-5TS uses the hydraulic
buffer and is not the same procedure as the one in ALPHA-SAF-OC5T-INS-1. The
short travel crane has no documented travel limit adjustment procedure in this
document collection. Raise a documentation request before adjusting any limit
on an OC-5TS.

## Documentation gaps

Not contained in this manual:

- The brake shim figures and the brake air gap for the hoist brakes. They are
  on the brake data sheet, which is not in this document collection.
- The rope drum grooving data and the rope replacement procedure. The
  replacement procedure is AM-PM-OC5T-ROPE, which is not in this collection.
- The wire rope certificate requirements and the discard counter reading
  procedure.
- The ultrasonic rope inspection acceptance criteria. The inspection is
  performed by the contracted inspection service and the acceptance
  thresholds are in the service specification, not in this manual.
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

## Appendix: Structural inspection and weld criteria

The crane structure is inspected for cracking, corrosion and deformation. The
welds are the highest-risk locations because they carry the cyclic load of
every lift. The inspection covers the runway, the end carriage, the bridge,
the trolley and the hoist mounting.

| Location | What to look for | Acceptance criterion |
| --- | --- | --- |
| Runway rail | Wear, misalignment, loose clips | Wear below 10 percent, rail straight |
| End carriage | Cracks at the wheelbox | No cracks; weld repair before use |
| Bridge girders | Cracks at the web stiffeners | No cracks; repair before use |
| Trolley frame | Cracks at the wheel mounts | No cracks |
| Hoist mounting | Bolt torque, cracks | Torque per drawing, no cracks |
| Festoon and cable | Chafing, broken clips | No exposed conductors |
| Pendant and cable | Strain relief, cuts | No exposed conductors, relief intact |

A crack found in a primary structural member stops the crane. The crack is
repaired to an approved welding procedure by a qualified welder, and the crane
is proof loaded before it is returned to service.

Corrosion is assessed by the loss of section. A member that has lost more than
10 percent of its thickness is repaired or replaced. Surface rust with no loss
of section is cleaned and repainted.

## Appendix: Operator controls and pre-use checks

The operator performs a pre-use check at the start of every shift. The check
is short but it is the last chance to catch a fault before a load is lifted
over people or equipment.

Pre-use checks:

- Confirm the pendant is undamaged and the buttons return when released.
- Confirm the emergency stop stops all motion and latches.
- Confirm the hoist brake holds the empty hook without drift.
- Confirm the upper and lower limit switches stop the hoist.
- Confirm the trolley and bridge travel smoothly in both directions.
- Confirm the overload indicator is working and not latched.
- Confirm the load chain or rope is free of visible damage.
- Confirm the runway is clear of people and obstructions.

Any check that fails is reported and the crane is taken out of service. A
crane with a failed brake, limit switch or emergency stop is not used, even
for a single lift. The defect is recorded and the crane is tagged out until it
is repaired and re-checked.

## Appendix: Rope, hook and brake reference data

| Item | Value | Source |
| --- | --- | --- |
| Rope construction | 6 x 36 wire rope, fibre core | rating plate |
| Rope diameter | 13 mm | rating plate |
| Minimum breaking load | 98 kN | supplier certificate |
| Discard, broken wires in one lay | 6 | this manual |
| Discard, reduction in diameter | 10 percent of nominal | this manual |
| Discard, kink or birdcage | any visible kink or birdcage | this manual |
| Hook opening, maximum | 15 percent increase over new | hook gauge |
| Hook throat wear, maximum | 10 percent of new dimension | hook gauge |
| Brake test load | 110 percent of safe working load every 6 months | this manual |
| Brake lining minimum thickness | 2 mm | brake maker |
| Limit switch repeatability | within 10 mm | this manual |

The hook is examined with a gauge at every six-monthly inspection, not only
when wear is suspected. A hook that fails the gauge is removed from service and
is never reworked by welding or grinding. Distortion of the hook, cracks at the
throat and any twist are rejection conditions regardless of the measured wear.

Rope inspection records the number of broken wires in the worst lay over the
whole length, the position of the worst section and the diameter at that
section. The position is recorded against the runway so that the next
inspection can compare the same place. Surface rust that can be removed with a
rag is not a rejection condition; pitting or a reduction in diameter is.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2022-11-01 | First controlled issue after the crane replacement in Bay 5. |
| Rev B | 2025-02-10 | 2024 rope inspection campaign and brake failure review. Tighter rope discard criterion, lower deflection limit, reduced hoist speed above 3.0 t, six monthly non-destructive testing and brake tests. |
