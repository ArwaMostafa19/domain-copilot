---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-MAN-HP200-A"
source_id: "AM-DOC-1042"
title: "ALPHA-HP-200 Hydraulic Press - Equipment Manual"
equipment: "ALPHA-HP-200"
equipment_also_covers: "ALPHA-HP-200B (variant differences listed under Variant coverage)"
document_type: "equipment-manual"
document_type_name: "Equipment manual"
revision: "Rev A"
effective_date: "2023-03-01"
status: "superseded"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-SAF-HP200-LOTO-1, ALPHA-PM-HP200-A, ALPHA-DIA-P100-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-HP-200 Hydraulic Press - Equipment Manual

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-MAN-HP200-A |
| Source identifier | AM-DOC-1042 |
| Equipment | ALPHA-HP-200 |
| Also covers | ALPHA-HP-200B (variant differences listed under Variant coverage) |
| Document type | Equipment manual |
| Revision | Rev A |
| Effective date | 2023-03-01 |
| Status | superseded |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-SAF-HP200-LOTO-1, ALPHA-PM-HP200-A, ALPHA-DIA-P100-1 |
| Document owner | Maintenance Engineering |

## Purpose

This manual describes the design, rated limits and safe operation of the
ALPHA-HP-200 four-post hydraulic press (serial range 2004-1xx) installed in
Bay 2 of Ridgeway Works.

It is the controlled reference that maintenance technicians use when they build
a work order for this press. Every set point, torque and interval stated here is
authorised for this press only. Values taken from another press, from the
as-built drawings, from a vendor brochure or from memory are not authorised
values and must not be substituted.

This manual does not cover the following equipment:

- ALPHA-HP-210, the 1000 kN bench press. It has a different frame, a different
  relief valve set point and a different guard arrangement. It has its own
  manual, AM-MAN-HP210.
- ALPHA-HP-200B, an ALPHA-HP-200 with the 300 mm extended ram kit fitted. The
   differences are listed under Variant coverage. A work order that ignores those
  differences is a defective work order.

## Equipment overview

The press is a four-post, single-ram unit fed from hydraulic power unit
ALPHA-P-100 (30 kW, fixed displacement pump, 63 l/min). The ram is located and
guided by four tie rods and four adjustable gib blocks; ram parallelism is
maintained by adjusting the gib blocks, not by the hydraulic system.

Tooling is supported on an upper bolster carried by the ram and a fixed lower
bolster. Both bolsters are T-slotted on 36 mm centres. Tool holding is by
bolster clamping screws; the press has no die cushion, so the tool and the
closed ram are left under full stored load whenever the ram is down. The
counterbalance cylinders hold the ram weight only while the pump is running.

Control is a hard-wired pendant with a monitored two-hand control, a safety
relay cabinet in panel 3A-04 and a mechanical die height sensor on the ram.
There is no closed-loop position control; ram position is derived from the
sensor, not from the valve.

## Technical data

| Parameter | Value |
| --- | --- |
| Rated press force at full daylight | 2000 kN |
| Relief valve set point (main circuit) | 240 bar |
| Maximum permissible working pressure | 235 bar |
| Hard-wired high pressure trip | 250 bar |
| Secondary (tool clamp) circuit set point | 180 bar |
| Rated capacity daylight | 1200 mm |
| Stroke | 800 mm |
| Die closing height | 120 mm minimum, 1100 mm maximum |
| Bed size | 1400 mm x 1200 mm, T-slots on 36 mm centres |
| Ram speed, approach | 60 mm/s |
| Ram speed, working | 25 mm/s |
| Ram speed, final 25 mm of stroke | 10 mm/s maximum |
| Motor | 30 kW, 400 V, three phase, 1460 rpm |
| Pump | fixed displacement, 63 l/min |
| Hydraulic oil | ISO VG 46 mineral, Alpha specification AM-H46 |
| Reservoir | 260 l, sight gauge plus high and low level switches |
| Return line filtration | 10 micron, element AM-FL-10 |
| Tie-rod nut torque | 340 N.m, re-torque every 4000 running hours |
| Die height sensor calibration | every 1000 running hours |
| Hydraulic oil analysis | every 500 running hours |
| Ram parallelism | 0.5 mm maximum per metre of die face |
| Mass | 4200 kg |
| Noise at operator position | 82 dB(A) during working stroke |

Running hours are read from the hour meter at the pendant. The hour meter
counts only while the pump motor is energised; it does not count standby time.

## Operating conditions

- Ambient air temperature: 5 degC to 35 degC. The press must not be started
  with oil temperature below 15 degC; warm the oil with the pump in bypass.
- Hydraulic oil temperature: 20 degC to 55 degC continuous. Above 60 degC the
  oil viscosity drops below the value the seals depend on.
- The press is rated for indoor, non-corrosive service. It must not be used
  outdoors or in a wash-down area.
- The press may be used for pressing, coining, rivet setting and plastic
  compression up to 120 degC tool temperature. Hot forging, welding and any
  operation that puts sparks near the ram seals is prohibited.
- Maximum tool mass per station is 250 kg. Heavier tools must be handled with
  the overhead crane ALPHA-OC-5T and a spreader beam; the bolster clamp screws
  must not be used to lift anything.
- Maximum combined tool height is limited by the 1100 mm die closing height.
  A tool set-up that leaves less than 120 mm die closing height must be
  re-calculated by Maintenance Engineering before use.

## Safeguards and control system

- Two-hand control: monitored, safety-rated, mounted so that both hands must
  be detected within the same 600 ms window. The minimum hold-to-run time is
  600 ms; releasing either hand before 600 ms must not produce any ram motion.
- Safety-rated stop time, controls to ram stop: 250 ms maximum.
- Performance level of the two-hand control and the stop function: category 3,
  PL d, per the press safety circuit assessment.
- Upper ram stop switch and lower ram stop switch are independent of the
  die height sensor.
- Die height sensor: mechanical plunger type, part AM-DHS-22. It is a
  protective measure, not a positioning device.
- Counterbalance pressure must be present before the main relief opens. Loss
  of counterbalance with the ram down causes the ram to drop.
- The two-hand control must never be defeated, jumpered, taped over or bridged.
  Any diagnostic that requires defeating the safety circuit needs a documented
  risk assessment, a permit and a second authorised person present.

## Operating limits and permitted range

1. Working pressure must not exceed 235 bar at the manifold. The relief valve
   is set at 240 bar and is not adjustable in service. Any requirement to
   reduce pressure is raised as a work order for Maintenance Engineering.
2. Pressing force is limited to 2000 kN at 1200 mm daylight. The force falls
   off as the die closes, because the pressure transducer used for the
   displayed force is calibrated for full daylight. Do not use the displayed
   force as a control value during a low daylight operation.
3. Point loading outside the bolster T-slots is not permitted. The load must
   be spread over the bolster area.
4. The ram must not be left resting on a tool with the pump stopped unless the
   tool is mechanically locked, because a loss of counterbalance with the pump
   stopped allows the ram to descend.
5. Ram parallelism must be within 0.5 mm per metre of die face before a
   precision operation. An operation that would damage the tool if the press
   is out of parallelism must not start until the ram parallelism check in
   Maintenance and inspection requirements is complete and recorded.

## Routine operator checks before use

Performed by the operator, in this order, before the first cycle of a shift:

1. Check the reservoir oil level on the sight gauge. The oil must be between
   the two marks. A low level is a stop condition, not a top-up condition.
2. Check that there is no oil on the floor under the press, the power unit or
   the manifold. Any leakage is reported before the press is used.
3. Check that the tie rods, gib blocks, bolsters and the ram crown are free of
   visible damage and that no tools or scrap are inside the die area.
4. Check the two-hand control: operate it with the press in manual, confirm
   the safety relay reports a healthy chain in the diagnostics menu.
5. Confirm the die height sensor reading against the mechanical position
   indicator on the ram with the ram at the upper stop.
6. Run three complete cycles with the die area empty and observe the ram for
   side movement. More than 2 mm of side movement is a stop condition.
7. Check the audible warning and the emergency stop at the pendant.

Any failed check means the press is not released for production. Raise a work
order and apply the isolation requirement in ALPHA-SAF-HP200-LOTO-1 if the ram,
the bolsters or the hydraulic circuit have to be touched.

## Variant coverage

ALPHA-HP-200B is an ALPHA-HP-200 retrofitted with the 300 mm extended ram kit
(kit AM-KIT-R300). If the asset plate on the press carries the suffix B, the
following values differ from Technical data and Variant coverage in this manual:

| Parameter | ALPHA-HP-200 | ALPHA-HP-200B |
| --- | --- | --- |
| Rated daylight | 1200 mm | 1500 mm |
| Stroke | 800 mm | 800 mm |
| Tie-rod nut torque | 340 N.m | 390 N.m |
| Tie-rod re-torque interval | 4000 running hours | 3000 running hours |
| Bolsters required | standard HP-BOL-12 | HP-BOL-15 |
| Pressing force at full daylight | 2000 kN | 2000 kN |

Using the 340 N.m figure on an HP-200B is a recognised cause of tie-rod
failure. If the asset plate is missing or unreadable, stop and raise a work
order; do not guess the variant.

ALPHA-HP-210 is not a variant of this press and nothing in this manual applies
to it. See AM-MAN-HP210.

## Maintenance and inspection requirements

The full preventive maintenance programme is in AM-PM-HP200. The items below
are the limits from this manual that the programme must satisfy:

- Hydraulic oil analysis every 500 running hours.
- Tie-rod re-torque every 4000 running hours.
- Die height sensor calibration every 1000 running hours.
- Ram parallelism check every 2000 running hours.
- Structural inspection of the four post welds every 6000 running hours.

Work on the hydraulic circuit, the bolsters, the tie rods or the ram requires
the zero-energy state defined in ALPHA-SAF-HP200-LOTO-1 first. There is no task
in this manual that may be started while the circuit is charged.

## Documentation gaps

The following values are not contained in this manual. They are recorded on
the as-built documentation held by Maintenance Engineering and that
documentation is not part of this document collection:

- Gib block and wedge clearance setting for this serial number: recorded on
  commissioning sheet CM-HP200-01.
- Manifold fitting torque values: on the fitting vendor data sheets, not in
  this document.
- Accelerometer alarm thresholds used by the optional ram monitoring system:
  set in the condition monitoring configuration, not in this manual.
- Nitrogen pre-charge pressure of accumulator AC-1: as-built, see
  ALPHA-SAF-HP200-LOTO-1 required sequence, accumulator bleed-down step, for the
  bleed-down requirement.

If a technician needs one of these values and cannot read it from the
controlled documents available at the machine, the correct action is a work
order with documentation status "insufficient information", not a measured
substitute.

## Escalation conditions

Escalate immediately, before continuing the diagnosis, when any of the
following occurs:

- Hydraulic pressure above 235 bar with no tooling load in the die.
- Audible knocking from the pump that does not stop when the relief opens.
- Visible hydraulic oil in the die area, on the tie rods or inside the frame.
- Ram side movement above 2 mm, or a parallelism reading outside 0.5 mm per
  metre.
- Any broken wire, cracked bolster clamp or damaged guard discovered during an
  inspection.
- Repeated tripping of the safety circuit on the same cycle of the two-hand
  control.
- A required value is missing from the controlled document set.

Escalation route: Level 2 Maintenance Engineering, then the Production
Supervisor, then EHS for anything involving stored energy or structural
damage.

## Appendix: Recommended spares and consumables

The following spares are held for the ALPHA-HP-200 press. Quantities are the
minimum stock for a single unit; increase them if a second press shares the
same hydraulic power unit. Consumables are listed with the approved
specification so that a substitute is never fitted without engineering
approval.

| Item | Part or specification | Minimum stock | Replacement interval |
| --- | --- | --- | --- |
| Main relief valve cartridge | RV-200-A, 240 bar setting | 1 | On failure or at overhaul |
| Counterbalance valve | CB-200, pilot ratio 4.5:1 | 1 | On failure |
| Ram seal kit | SK-200-80, nitrile and PTFE | 2 | At 8000 running hours or on leak |
| Gib wear strip set | GW-200, bronze faced | 1 set | At 12000 running hours |
| Suction strainer element | 63 micron, 63 l/min | 2 | Every 1000 running hours |
| Return filter element | 10 micron absolute | 3 | Every 500 running hours |
| Accumulator bladder | AC-1, 6 l, nitrogen | 1 | Every 5 years |
| Pressure transducer | 0 to 400 bar, 4 to 20 mA | 1 | On calibration failure |
| Two-hand control relay | Category 4 safety relay | 1 | On proof-test failure |
| Limit switch | IP67, roller lever | 2 | On failure |
| Hydraulic oil | ISO VG 46, AM-H46 | 520 l | Every 2000 hours or on analysis |
| Way lubricant | ISO VG 68 | 20 l | Top up as required |

Spares fitted must be recorded on the work order with the part number and the
asset serial number. A spare whose specification differs from the table is a
non-conformance and must be raised with Maintenance Engineering before fitting.

## Appendix: Commissioning and first-start checks

This appendix lists the checks required after any work that opens the
hydraulic circuit, disturbs the frame or replaces a safety device. The checks
are performed in order and the measured value is recorded, not a pass or fail
mark. Work that has not been through this sequence is not returned to
production.

1. Confirm the reservoir is filled to the mid to high mark with ISO VG 46 oil
   and that the suction strainer and return filter are new or proven.
2. Confirm every frame fastener is torqued to the values in the technical data
   table and that the tie-rod nuts are re-torqued if the frame was disturbed.
3. Confirm the accumulator AC-1 is charged to its specified nitrogen
   pre-charge and that the safety block is open.
4. Run the pump with the relief valve backed off and confirm the pump develops
   pressure smoothly with no cavitation noise. Record suction pressure.
5. Set the main relief valve to 240 bar using a calibrated gauge at test point
   TP-3. Record the lift-off and reseat pressure.
6. Confirm the hard-wired high-pressure trip operates at 250 bar and that the
   circuit cannot be reset below 230 bar.
7. Confirm the two-hand control holds for 900 ms and that releasing either
   button stops the ram within the documented stopping performance.
8. Confirm the light curtain and guard interlocks stop the ram when broken and
   that the press cannot be restarted until the guard is closed and reset.
9. Cycle the press ten times at working speed and confirm the ram stops at the
   bottom of the stroke without drift for five minutes.
10. Record oil temperature at the end of the run and confirm it is below the
    alarm set point.

Every value is entered on the commissioning record and countersigned by the
person who authorized the work.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2023-03-01 | First controlled issue for ALPHA-HP-200 after the 2023 press rebuild. |
