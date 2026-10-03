---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-MAN-OC5T-B"
source_id: "BM-DOC-2275"
title: "BETA-OC-5T Overhead Travelling Crane - Equipment Manual"
equipment: "BETA-OC-5T"
equipment_also_covers: "BETA-OC-5TS and BETA-OC-5TL (variant differences listed under Variant coverage)"
document_type: "equipment-manual"
document_type_name: "Equipment manual"
revision: "Rev B"
effective_date: "2025-03-01"
status: "current"
supersedes: "BETA-MAN-OC5T-A"
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
| Document identifier | BETA-MAN-OC5T-B |
| Source identifier | BM-DOC-2275 |
| Equipment | BETA-OC-5T |
| Also covers | BETA-OC-5TS and BETA-OC-5TL (variant differences listed under Variant coverage) |
| Document type | Equipment manual |
| Revision | Rev B |
| Effective date | 2025-03-01 |
| Status | current |
| Supersedes | BETA-MAN-OC5T-A |
| Applies to | Assets listed under equipment |
| Related documents | BETA-SAF-OC5T-INS-1, BETA-WO-RULES-1 |
| Document owner | Maintenance Engineering |

## Purpose

This manual describes the BETA-OC-5T single girder overhead travelling
crane, 5.0 tons safe working load at 59 ft span, serving Line 1 at Harbor
Works.

Rev B was issued after the 2024 hook block replacement and the review of two
near misses involving the radio pendant on Line 1.

All values are in imperial units unless stated otherwise on the line.

## Reason for this revision

The 2024 hook block on this crane was replaced because the thrust bearing
play exceeded the limit. The replacement block is 6 in taller than the original
block, which reduced the available hook height and required the upper hoist
limit to be lowered.

The two pendant near misses were caused by an operator carrying the pendant
outside the marked control zone while the crane was moving. Rev B therefore
adds an active control zone check and a weekly pendant test requirement, and
limits hoist speed for heavier loads.

## Equipment overview

Single girder crane, underhung hook block, two-fall reeving, two trolley
drives and one hoist drive. Power supply is a conductor bar system along the
runway beam.

The hoist gearbox has two brakes, spring applied and hydraulically released,
one on the motor shaft and one on the drum. The hoist is fail-safe: on loss of
power both brakes apply.

The crane is controlled by radio pendant only. There are no pendant sockets
along the runway. The radio pendant has an enable button, a large emergency
stop, five movement buttons and a control zone check function.

The runway consists of two rails on corbels with end stops, wheel buffers and
a runway limit switch at each end.

## Technical data

| Parameter | Value |
| --- | --- |
| Safe working load | 5.0 tons at 59 ft span |
| Maximum hook height | 11 ft 6 in |
| Hoist speed, raising, loads up to 2.0 tons | 26 ft/min |
| Hoist speed, raising, loads above 2.0 tons | 16 ft/min |
| Hoist speed, lowering | 26 ft/min |
| Trolley speed | 60 ft/min |
| Rope | 3/8 in 6x19 IWRC, grade 1770 N/mm2 |
| Rope discard criterion | 6 broken wires within 10 rope diameters |
| Maximum vertical deflection at mid span under rated load | 22 mm |
| Brake holding torque requirement | 150 percent of rated torque |
| Brake test load | 110 percent of safe working load |
| Brake test interval | 6 months |
| Proving period | 12 months |
| Hoist limit switch | upper only, at 11 ft 6 in |
| Runway limit switches | one per end of travel |
| Control | radio pendant, active control zone check |
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
7. The radio pendant must be tested before use each shift, and the control
   zone check must pass, before the crane may move. A pendant that does not
   pass is removed from service and swapped for a spare.
8. The operator must be inside the marked control zone on the floor for all
   movements. The control zone is marked in yellow on the floor of the bay and
   covers the full travel of the trolley.
9. For loads above 2.0 tons the reduced hoist speed in Technical data is selected
   before the load is lifted.

## Brake system

- Holding brake on the motor shaft, spring applied, hydraulically released.
- Second brake on the drum, spring applied, released by the same circuit.
- Both brakes must release together. Partial release is a stop condition.
- Brake setting is a maintenance task. The shim figures and the release air
  gap are on the brake data sheet, which is not reproduced here and is not part
  of this document collection.
- A brake that slips under load is not a fault to be monitored. The crane is
  taken out of service and the load is lowered under control.
- A partial brake release is treated as a load handling incident and is
  reported to EHS.

## Inspection and testing requirements

- Daily operator pre-use inspection: see BETA-SAF-OC5T-INS-1.
- Weekly radio pendant self test and no-load functional test of hoist, travel
  and all limits with the hook empty.
- Monthly documented inspection of ropes, hook, hook latch, limits, brakes and
  the electrical enclosure.
- Six monthly brake test at 110 percent of safe working load with calibrated
  test weights.
- Six monthly magnetic particle inspection of the hook and the hook nut, and
  six monthly ultrasonic rope inspection by the contracted service.
- Annual thorough examination by a competent person.

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
| Maximum hook height | 11 ft 6 in | 8 ft 0 in | 11 ft 6 in |
| Discard criterion | as Technical data | as Technical data | as Technical data |

The short travel crane has no documented travel limit adjustment procedure in
this document collection, and its hook height is 8 ft 0 in because it runs on
a different runway beam. Do not apply the hook height in Technical data to an
OC-5TS.

## Documentation gaps

Not contained in this manual:

- The brake shim figures and the release air gap, which are on the brake data
  sheet.
- The rope drum grooving data and the rope replacement procedure,
  BM-PM-OC5T-ROPE, which is not in this collection.
- The wire rope certificate requirements.
- The radio pendant frequency plan and the control zone dimensions.
- The load test weight calibration certificates, which are in the lifting
  equipment register.
- The upper hoist limit adjustment procedure, BM-PM-OC5T-LIMIT.

## Escalation conditions

Stop using the crane and escalate to Maintenance Engineering and EHS when:

- Any brake slips, or the load lowers without command.
- Any wire rope defect, broken wire, birdcaging, kinks or corrosion.
- The hook, hook nut or hook latch is deformed, worn or cracked.
- A limit switch fails to operate, or operates at the wrong point.
- The radio pendant self test or the control zone check fails.
- Vertical deflection under a static test load exceeds the limit in Technical data.
- A required figure is not in the controlled document set.

## Appendix: Structural inspection and weld criteria

The crane structure is inspected for cracking, corrosion and deformation. The
welds are the highest-risk locations because they carry the cyclic load of
every lift.

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

The operator performs a pre-use check at the start of every shift. It is the
last chance to catch a fault before a load is lifted over people or equipment.

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
for a single lift.

## Appendix: Rope, hook and brake reference data

| Item | Value | Source |
| --- | --- | --- |
| Rope construction | 6 x 36 wire rope, fibre core | rating plate |
| Rope diameter | 1/2 in | rating plate |
| Minimum breaking load | 11 tons | supplier certificate |
| Discard, broken wires in one lay | 6 | this manual |
| Discard, reduction in diameter | 10 percent of nominal | this manual |
| Discard, kink or birdcage | any visible kink or birdcage | this manual |
| Hook opening, maximum | 15 percent increase over new | hook gauge |
| Hook throat wear, maximum | 10 percent of new dimension | hook gauge |
| Brake test load | 110 percent of safe working load every 6 months | this manual |
| Brake lining minimum thickness | 3/32 in | brake maker |
| Limit switch repeatability | within 1/2 in | this manual |

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
| Rev A | 2022-12-05 | First controlled issue after the radio control retrofit on Line 1. |
| Rev B | 2025-03-01 | 2024 hook block replacement and pendant near miss review. Lowered hook height and upper hoist limit, reduced hoist speed above 2.0 tons, tightened rope discard criterion and deflection limit, added six monthly brake and non-destructive tests. |
