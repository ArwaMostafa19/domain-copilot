---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-MAN-HP200-A"
source_id: "BM-DOC-2204"
title: "BETA-HP-200 Hydraulic Press - Equipment Manual"
equipment: "BETA-HP-200"
equipment_also_covers: "none; the HP-200S straight-side variant is out of scope, see Documentation gaps"
document_type: "equipment-manual"
document_type_name: "Equipment manual"
revision: "Rev A"
effective_date: "2023-01-20"
status: "superseded"
supersedes: ""
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BETA-SAF-HP200-ECP-1, BETA-PM-HP200-A, BETA-DIA-P100-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-HP-200 Hydraulic Press - Equipment Manual

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-MAN-HP200-A |
| Source identifier | BM-DOC-2204 |
| Equipment | BETA-HP-200 |
| Also covers | none; the HP-200S straight-side variant is out of scope, see Documentation gaps |
| Document type | Equipment manual |
| Revision | Rev A |
| Effective date | 2023-01-20 |
| Status | superseded |
| Applies to | Assets listed under equipment |
| Related documents | BETA-SAF-HP200-ECP-1, BETA-PM-HP200-A, BETA-DIA-P100-1 |
| Document owner | Maintenance Engineering |

## Purpose

This manual describes the design, rated limits and safe operation of the
BETA-HP-200 H-frame hydraulic press, 160 tons, installed on Line 1 at Harbor
Works.

It is the controlled reference used when building a work order for this press.
Every set point, torque and interval stated here is authorised for this press
only.

All values in this manual are in imperial units: psi, inches, lbf.ft and gpm.
Do not convert a value into metric and act on the converted figure. A converted
figure is not a documented figure and the work order must record the imperial
value and the revision it came from.

This manual does not cover:

- BETA-HP-200S, the straight-side variant of this press. It has a different
  frame, a different clamp arrangement and a different guard. It is serviced
  under work instruction WI-2204.
- BETA-HP-250, the 250 ton straight-side press on Line 2.
- BETA-HP-100, the 100 ton bench press in the maintenance shop.

## Equipment overview

The BETA-HP-200 is a single H-frame press with a side mounted hydraulic power
unit, a 25 mm die cushion on the ram and a light curtain across the front of
the die area. Tooling is clamped by two hydraulic tool clamps on the lower
bolster.

The die cushion stores energy: it is a gas or oil filled cylinder that is
compressed when the ram descends through the last inch of stroke. The cushion
pressure must be released and the cushion cylinder blocked before anyone
enters the die area.

Guard interlocks are on the front sliding guard. The press cannot cycle with
any guard open, and muting of the light curtain is prohibited on this machine.

## Technical data

| Parameter | Value |
| --- | --- |
| Rated press force | 160 tons at 32 in daylight |
| Relief valve set point, main circuit | 2000 psi |
| Maximum permissible working pressure | 1900 psi |
| Hard-wired high pressure trip | 2100 psi |
| Minimum hydraulic clamp pressure | 1500 psi |
| Rated capacity daylight | 32 in |
| Stroke | 24 in |
| Die cushion stroke | 1 in |
| Die closing height | 6 in minimum, 46 in maximum |
| Bed size | 42 in x 34 in, T-slots on 4 in centres |
| Ram speed, approach | 4 in/s |
| Ram speed, working | 2 in/s |
| Ram speed at die entry | 5 in/s maximum |
| Motor | 25 hp, 460 V, three phase |
| Pump | duplex, 30 gpm, two pumps P-100A and P-100B |
| Hydraulic oil | ISO VG 46 anti-wear hydraulic oil, Beta specification BM-H46 |
| Reservoir | 180 gal, sight glass and float switches |
| Return line filtration | 10 micron |
| Tie-rod nut torque | 2200 lbf.ft, re-torque every 3000 running hours |
| Die height sensor calibration | every 4000 running hours |
| Pressure gauge calibration | every 4000 running hours |
| Hydraulic oil analysis | every 1000 running hours |
| Ram parallelism | 0.008 in maximum per 12 in of die face |
| Ram parallelism check | every 2000 running hours |
| Sound pressure at the operator station | 88 dB(A) during the working stroke |

Running hours are read from the hour meter at the operator station. The hour
meter counts only while the pump motor is energised.

## Operating conditions

- Ambient air temperature: 40 degF to 104 degF. The press must not be started
  with oil temperature below 50 degF; warm the oil with the pumps in bypass.
- Hydraulic oil temperature: 68 degF to 131 degF continuous.
- Indoor, non-corrosive service only. Do not use the press in the wash-down
  bay or outdoors.
- Permitted operations: stamping, coining, rivet setting and plastic
  compression. Forging, welding and any operation that puts sparks near the
  seals is prohibited.
- Maximum tool weight is 500 lb. Heavier tools are handled with the
  BETA-OC-5T crane using a spreader beam.
- Sound levels above 85 dB(A) require hearing protection, which is posted at
  the press and included in the line hearing protection plan.

## Safeguards and control system

- Light curtain across the front of the die area, safety rated, category 3,
  PL d. Muting is prohibited on this press. There is no muting function in the
  control software and enabling one is an unauthorised modification.
- Safety-rated stop time, light curtain beam to ram stop: 200 ms maximum.
- Hold-to-run time: 700 ms minimum. Releasing the cycle button before 700 ms
  must not produce any ram motion.
- Two independent ram position limit switches plus an anti-two-block contact.
- Tool clamps must be at the minimum clamp pressure in Technical data before the
  ram can descend. The interlock is defeated when the pressure switch does not
  prove; a press that will not hold clamp pressure must not be used.
- The light curtain must never be defeated, taped over, blocked or bypassed
  with an opaque object. Any diagnostic that requires defeating the safety
  circuit requires a documented risk assessment, a written permit and a second
  authorised person present.

## Operating limits and permitted range

1. Working pressure must not exceed 1900 psi at the manifold. The relief
   valve is set at 2000 psi and is not adjustable in service. A requirement
   to change a set point is raised as a work order for Maintenance
   Engineering.
2. Pressing force is limited to 160 tons at 32 in daylight. The displayed
   force falls off as the die closes because the transducer is calibrated for
   full daylight.
3. Point loading outside the bolster T-slots is prohibited.
4. The die cushion must be at its rated pressure before the ram is lowered.
   Operating with the cushion disabled risks tool damage and is prohibited.
5. Ram parallelism must be within 0.008 in per 12 in of die face before a
   precision operation.

## Routine operator checks before use

Performed by the operator before the first cycle of a shift:

1. Check the reservoir oil level on the sight glass. A low level is a stop
   condition, not a top-up condition.
2. Check for oil on the floor under the press, under the power unit and
   around the cushions.
3. Check the light curtain is free of obstruction and that the columns and
   emitters are clean.
4. Confirm the safety relay diagnostics show a healthy chain.
5. Run three complete cycles with the die area empty and observe the ram for
   side movement. More than 0.08 in of side movement is a stop condition.
6. Confirm the hydraulic clamp pressure indication is at or above the minimum
   in Technical data.
7. Check the audible warning and the emergency stop at the operator station.

Any failed check means the press is not released for production.

## Variant coverage

| Parameter | BETA-HP-200 | BETA-HP-200S straight-side |
| --- | --- | --- |
| Rated force | 160 tons | 160 tons |
| Frame | H-frame | Straight-side |
| Daylight | 32 in | 32 in |
| Hydraulic clamp pressure, minimum | 1500 psi | 1800 psi |
| Sound pressure at the operator station | 88 dB(A) | 85 dB(A) |
| Guard arrangement | sliding front guard, light curtain | fixed guard, light curtain |

BETA-HP-200S is serviced under work instruction WI-2204. That instruction is
not part of this document collection. If the asset plate carries the suffix S,
stop and raise a documentation request before any work on the clamp circuit,
the guard or the cushion.

BETA-HP-250 is a different machine with a 250 ton rating and different limits.
BETA-HP-100 is a bench press in the maintenance shop. Neither is covered here.

## Maintenance and inspection requirements

The preventive maintenance programme is in BM-PM-HP200. The limits from this
manual that the programme must satisfy:

- Hydraulic oil analysis every 1000 running hours.
- Tie-rod re-torque every 3000 running hours.
- Die height sensor calibration every 4000 running hours.
- Pressure gauge calibration every 4000 running hours.
- Ram parallelism check every 2000 running hours.

Work on the hydraulic circuit, the cushions, the bolsters, the tie rods or the
frame requires the energy control state defined in BETA-SAF-HP200-ECP-1 first.

## Documentation gaps

The following values are not contained in this manual. They are held in the
as-built records, which are not part of this document collection:

- Die cushion gas or oil charge pressure for this serial number: on the
  commissioning sheet CM-HP200-01.
- Clamp cylinder and cushion cylinder seal part numbers.
- Manifold and tube fitting torque values: on the fitting vendor data sheets.
- The work instruction WI-2204 that covers the HP-200S straight-side variant.

If a technician needs one of these values and cannot read it from the
controlled documents available at the machine, the correct action is a work
order with documentation status "insufficient information", not a measured
substitute.

## Escalation conditions

Escalate immediately, before continuing the diagnosis, when any of the
following occurs:

- Hydraulic pressure above 1900 psi with no tooling load in the die.
- An audible knock from the pump that does not stop when the relief opens.
- Visible hydraulic oil in the die area, on the tie rods or inside the frame.
- Ram side movement above 0.08 in, or a parallelism reading outside 0.008 in
  per 12 in.
- Hydraulic clamp pressure below the minimum in Technical data.
- Any crash of the light curtain during a cycle.
- A repeated trip of the safety circuit on the same cycle.
- A required value is missing from the controlled document set.

Escalation route: Level 2 Maintenance Engineering, then the Line 1
Supervisor, then EHS for anything involving stored energy or structural
damage.

## Appendix: Recommended spares and consumables

The following spares are held for the BETA-HP-200 press. Quantities are the
minimum stock for a single unit. Consumables are listed with the approved
specification so that a substitute is never fitted without engineering
approval.

| Item | Part or specification | Minimum stock | Replacement interval |
| --- | --- | --- | --- |
| Main relief valve cartridge | RV-200-B, 2000 psi setting | 1 | On failure or at overhaul |
| Counterbalance valve | CB-200, pilot ratio 4.5:1 | 1 | On failure |
| Ram seal kit | SK-200-80, nitrile and PTFE | 2 | At 8000 running hours or on leak |
| Gib wear strip set | GW-200, bronze faced | 1 set | At 12000 running hours |
| Suction strainer element | 63 micron, 16 gpm | 2 | Every 1000 running hours |
| Return filter element | 10 micron absolute | 3 | Every 500 running hours |
| Accumulator bladder | AC-1, 1.6 gal, nitrogen | 1 | Every 5 years |
| Pressure transducer | 0 to 5800 psi, 4 to 20 mA | 1 | On calibration failure |
| Two-hand control relay | Category 4 safety relay | 1 | On proof-test failure |
| Limit switch | IP67, roller lever | 2 | On failure |
| Hydraulic oil | ISO VG 46, BM-H46 | 140 gal | Every 2000 hours or on analysis |
| Way lubricant | ISO VG 68 | 5 gal | Top up as required |

Spares fitted must be recorded with the part number, the asset serial number
and the person who fitted them.

## Appendix: Commissioning and first-start checks

This appendix lists the checks required after any work that opens the
hydraulic circuit, disturbs the frame or replaces a safety device. Checks are
performed in order and the measured value is recorded.

1. Confirm the reservoir is filled to the mid to high mark with ISO VG 46 oil
   and that the strainer and filter are new or proven.
2. Confirm every frame fastener is torqued to the values in the technical data
   table and that the tie-rod nuts are re-torqued if the frame was disturbed.
3. Confirm the accumulator is charged to its specified nitrogen pre-charge.
4. Run the pump with the relief backed off and confirm smooth pressure with no
   cavitation noise.
5. Set the main relief valve to 2000 psi using a calibrated gauge at the test
   point. Record the lift-off and reseat pressure.
6. Confirm the high-pressure trip operates at its set point and cannot be
   reset below the lower bound.
7. Confirm the two-hand control holds for the documented time and that
   releasing either button stops the ram.
8. Confirm the guard interlocks stop the ram when broken.
9. Cycle the press ten times and confirm no drift at the bottom of the stroke.
10. Record the oil temperature at the end of the run.

Each value is entered on the commissioning record and countersigned.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2023-01-20 | First controlled issue for BETA-HP-200 after the Line 1 rebuild. |
