---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-MAN-HP200-B"
source_id: "BM-DOC-2204"
title: "BETA-HP-200 Hydraulic Press - Equipment Manual"
equipment: "BETA-HP-200"
equipment_also_covers: "none; the HP-200S straight-side variant is out of scope, see Documentation gaps"
document_type: "equipment-manual"
document_type_name: "Equipment manual"
revision: "Rev B"
effective_date: "2025-05-15"
status: "current"
supersedes: "BETA-MAN-HP200-A"
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BETA-SAF-HP200-ECP-1, BETA-PM-HP200-B, BETA-DIA-P100-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-HP-200 Hydraulic Press - Equipment Manual

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-MAN-HP200-B |
| Source identifier | BM-DOC-2204 |
| Equipment | BETA-HP-200 |
| Also covers | none; the HP-200S straight-side variant is out of scope, see Documentation gaps |
| Document type | Equipment manual |
| Revision | Rev B |
| Effective date | 2025-05-15 |
| Status | current |
| Supersedes | BETA-MAN-HP200-A |
| Applies to | Assets listed under equipment |
| Related documents | BETA-SAF-HP200-ECP-1, BETA-PM-HP200-B, BETA-DIA-P100-1 |
| Document owner | Maintenance Engineering |

## Purpose

This manual describes the design, rated limits and safe operation of the
BETA-HP-200 H-frame hydraulic press, 160 tons, installed on Line 1 at Harbor
Works.

It is the controlled reference used when building a work order for this press.

All values in this manual are in imperial units: psi, inches, lbf.ft and gpm.
Do not convert a value into metric and act on the converted figure. A converted
figure is not a documented figure and the work order must record the imperial
value and the revision it came from.

## Reason for this revision

Rev B was issued after the Q1 2025 Line 1 incident review and the 2025
reliability review. The incident review found one clamp circuit failure that
released a tool under load and one light curtain event caused by a badly fitted
replacement emitter.

The changes in Rev B are conservative: pressures are lower, the die entry speed
is lower, the hold-to-run time is longer and the inspection intervals are
shorter. Nothing in Rev B relaxes a limit.

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
| Relief valve set point, main circuit | 1750 psi |
| Maximum permissible working pressure | 1650 psi |
| Hard-wired high pressure trip | 1850 psi |
| Minimum hydraulic clamp pressure | 1800 psi |
| Rated capacity daylight | 32 in |
| Stroke | 24 in |
| Die cushion stroke | 1 in |
| Die closing height | 6 in minimum, 46 in maximum |
| Bed size | 42 in x 34 in, T-slots on 4 in centres |
| Ram speed, approach | 4 in/s |
| Ram speed, working | 2 in/s |
| Ram speed at die entry | 3 in/s maximum for daylight above 40 in, otherwise 5 in/s |
| Motor | 25 hp, 460 V, three phase |
| Pump | duplex, 30 gpm, two pumps P-100A and P-100B |
| Hydraulic oil | ISO VG 46 anti-wear hydraulic oil, Beta specification BM-H46 |
| Reservoir | 180 gal, sight glass and float switches |
| Return line filtration | 10 micron |
| Tie-rod nut torque | 2200 lbf.ft, re-torque every 1500 running hours |
| Tie-rod re-torque method | three passes in diagonal sequence |
| Die height sensor calibration | every 2000 running hours |
| Pressure gauge calibration | every 2000 running hours |
| Hydraulic oil analysis | every 500 running hours, and after any hose failure |
| Ram parallelism | 0.008 in maximum per 12 in of die face |
| Ram parallelism check | every 1000 running hours |
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
- Hold-to-run time: 1000 ms minimum. Releasing the cycle button before 1000 ms
  must not produce any ram motion.
- Two independent ram position limit switches plus an anti-two-block contact.
- Tool clamps must be at or above the minimum clamp pressure in Technical data
  before the ram can descend. The interlock is defeated when the pressure
  switch does not prove; a press that will not hold clamp pressure must not be
  used.
- The light curtain must never be defeated, taped over, blocked or bypassed
  with an opaque object. Any diagnostic that requires defeating the safety
  circuit requires a documented risk assessment, a written permit and a second
  authorised person present.
- Every replacement emitter, column or receiver must be function tested before
  the press is returned to production. An emitter that has been replaced and
  not function tested is an undocumented safety device.

## Operating limits and permitted range

1. Working pressure must not exceed 1650 psi at the manifold. The relief
   valve is set at 1750 psi and is not adjustable in service. A reading above
   1650 psi with an empty die is a stop condition: stop the press, do not
   adjust the relief valve, and raise a work order.
2. Pressing force is limited to 160 tons at 32 in daylight. The displayed
   force falls off as the die closes because the transducer is calibrated for
   full daylight.
3. Point loading outside the bolster T-slots is prohibited.
4. The die cushion must be at its rated pressure before the ram is lowered.
5. Ram parallelism must be within 0.008 in per 12 in of die face before a
   precision operation.
6. Any event in which the hard-wired high pressure trip operated is a
   structural inspection trigger.

## Variant coverage

| Parameter | BETA-HP-200 | BETA-HP-200S straight-side |
| --- | --- | --- |
| Rated force | 160 tons | 160 tons |
| Frame | H-frame | Straight-side |
| Daylight | 32 in | 32 in |
| Hydraulic clamp pressure, minimum | 1800 psi | 1800 psi |
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

- Hydraulic oil analysis every 500 running hours, and after any hose failure.
- Tie-rod re-torque every 1500 running hours, three diagonal passes.
- Die height sensor calibration every 2000 running hours.
- Pressure gauge calibration every 2000 running hours.
- Ram parallelism check every 1000 running hours.
- Structural inspection of the frame welds every 3000 running hours, and
  after any overload event.
- Reduced die entry speed for tools with daylight above 40 in.

## Documentation gaps

The following values are not contained in this manual. They are held in the
as-built records, which are not part of this document collection:

- Die cushion gas or oil charge pressure for this serial number: on the
  commissioning sheet CM-HP200-01.
- Clamp cylinder and cushion cylinder seal part numbers.
- Manifold and tube fitting torque values: on the fitting vendor data sheets.
- The work instruction WI-2204 that covers the HP-200S straight-side variant.
- The light curtain manufacturer service procedure, which covers the response
  time calculation for muting requests; muting is prohibited here in any case.

## Escalation conditions

Escalate immediately, before continuing the diagnosis, when any of the
following occurs:

- Hydraulic pressure above 1650 psi with no tooling load in the die.
- An audible knock from the pump that does not stop when the relief opens.
- Visible hydraulic oil in the die area, on the tie rods or inside the frame.
- Ram side movement above 0.08 in, or a parallelism reading outside 0.008 in
  per 12 in.
- Hydraulic clamp pressure below the minimum in Technical data.
- Any crash of the light curtain during a cycle.
- Any overload event in which the high pressure trip operated.
- Any repeated trip of the safety circuit on the same cycle.
- A required value is missing from the controlled document set.

Escalation route: Level 2 Maintenance Engineering, then the Line 1
Supervisor, then EHS for anything involving stored energy or structural
damage.

## Appendix: Revision B change impact assessment

Revision B changed the relief set point and the oil analysis interval from
Revision A. This appendix records the impact so that a technician holding an
older work order can see what must be re-checked.

| Change | Revision A | Revision B | Impact |
| --- | --- | --- | --- |
| Main relief set point | 2000 psi | 1750 psi | Reduce the setting and re-seal |
| Oil analysis interval | 500 running hours | 300 running hours | Update the PM schedule |
| Tie-rod re-torque interval | 4000 running hours | 2000 running hours | Update the PM schedule |
| Accumulator pre-charge | 72 psi | 72 psi | No change |

The relief valve change is the significant one. A press still set to 2000 psi
after the revision takes effect will exceed the maximum permissible working
pressure of the circuit and is a stop condition. The setting is verified at
every annual service and after any relief valve work.

Work orders raised before the Revision B effective date remain valid until
worked; a work order that specifies a superseded value must be reissued
against Revision B before the work starts.

## Appendix: Operator daily and weekly checks

Daily and weekly checks are the first line of defence against a failure found
later at a planned service. They are performed by the operator and
countersigned by the shift supervisor.

Daily checks before first start:

- Confirm the hydraulic oil level is between the low and high marks.
- Confirm the oil temperature is above 68 degF before full load.
- Confirm the guard and light curtain are in place and undamaged.
- Confirm the emergency stop is not latched and resets correctly.
- Confirm there is no oil on the floor or the bolster.
- Confirm the pressure gauge reads zero with the pump stopped.

Weekly checks:

- Confirm the gauge matches the controller within 70 psi.
- Confirm the tie-rod nuts show no movement against the witness marks.
- Confirm the gib bolts are tight and the ram moves without hesitation.
- Confirm the oil is clear and free of milky emulsion.
- Confirm the accumulator safety block is open and tagged.
- Confirm the pump and motor mounts are not loose.

Any check that fails is reported before the next shift. A failed safety check
stops the press until corrected and re-verified.

## Appendix: Torque and fastener reference

The values below apply to fasteners that are replaced or re-torqued during
maintenance of the BETA-HP-200 press. Torque is applied with a calibrated
torque wrench and the value is recorded on the work order. Lubricated threads
use the thread lubricant stated in the table; anti-seize paste is not used on
fasteners in the hydraulic circuit.

| Fastener | Size and thread | Grade | Torque | Thread condition |
| --- | --- | --- | --- | --- |
| Frame tie-rod nut | 1 5/8 in x 8 | 10.9 | 250 lbf.ft | dry, three diagonal passes |
| Crown and base bolt | 1 in x 8 | 10.9 | 575 lbf.ft | dry |
| Column foot bolt | 1 1/4 in x 7 | 8.8 | 450 lbf.ft | dry |
| Ram guide shoe bolt | 5/8 in x 11 | 8.8 | 140 lbf.ft | dry |
| Relief valve cartridge | 3/4 in x 16 | 8.8 | 45 lbf.ft | hydraulic oil film |
| Accumulator flange bolt | 1 in x 8 | 10.9 | 235 lbf.ft | hydraulic oil film |
| Pump mounting bolt | 1/2 in x 13 | 8.8 | 62 lbf.ft | dry |
| Manifold subplate bolt | 3/8 in x 16 | 12.9 | 40 lbf.ft | dry |
| Guard panel bolt | 5/16 in x 18 | 8.8 | 18 lbf.ft | dry |
| Light curtain bracket bolt | 1/4 in x 20 | 8.8 | 8 lbf.ft | dry |

Fasteners removed from a safety device are replaced, not reused. Frame
fasteners are reused only if the threads are undamaged and the shank is not
corroded; otherwise they are replaced with a fastener of the same grade. A
fastener that has been torqued past its yield, identified by a stretched shank
or a nut that turns freely after it has seated, is scrapped and the reason is
recorded. The tie-rod re-torque interval is the one stated in the technical
data table of the current revision of this manual.

## Appendix: Glossary of hydraulic and control terms

This glossary defines the terms used in this manual. It is written for a
technician who is competent in mechanical maintenance but not necessarily
familiar with the press control terminology.

- Accumulator: a pressure vessel that stores hydraulic energy in a compressed
  gas and smooths pressure peaks in the circuit.
- Counterbalance valve: a valve that holds a vertical load and controls its
  descent, fitted in the return line from the ram.
- Daylight: the open distance between the ram face and the bed with the ram
  fully retracted.
- Die cushion: an auxiliary hydraulic circuit that supports the workpiece
  during forming; the BETA-HP-200 has a die cushion.
- Hold-to-run: a control principle in which the motion continues only while
  the operator holds the command device.
- Lift-off pressure: the pressure at which a relief valve first opens and
  passes a measurable flow.
- Light curtain: an electro-sensitive protective device that stops the ram
  when the sensing field is broken.
- Muting: the deliberate suspension of a protective device during part of the
  machine cycle; muting is prohibited on this press.
- Pilot ratio: the ratio of the pilot pressure area to the main spool area in
  a piloted valve.
- Pre-charge: the nitrogen pressure in an accumulator with the hydraulic side
  depressurised and open to tank.
- Reseat pressure: the pressure at which a relief valve closes after opening;
  it is always below the lift-off pressure.
- Safe working load: the maximum load a lifting accessory or machine may carry,
  as marked on the rating plate.
- Zero-energy verification tag: the tag fitted after isolation and
  verification to record that the asset is in a de-energised and proven state.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2023-01-20 | First controlled issue for BETA-HP-200 after the Line 1 rebuild. |
| Rev B | 2025-05-15 | Q1 2025 incident review and 2025 reliability review. Reduced pressure limits and die entry speed, longer hold-to-run, higher minimum clamp pressure and shorter inspection intervals. |
