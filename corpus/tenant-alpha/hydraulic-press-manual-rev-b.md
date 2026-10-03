---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-MAN-HP200-B"
source_id: "AM-DOC-1042"
title: "ALPHA-HP-200 Hydraulic Press - Equipment Manual"
equipment: "ALPHA-HP-200"
equipment_also_covers: "ALPHA-HP-200B (variant differences listed under Variant coverage)"
document_type: "equipment-manual"
document_type_name: "Equipment manual"
revision: "Rev B"
effective_date: "2025-06-01"
status: "current"
supersedes: "ALPHA-MAN-HP200-A"
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-SAF-HP200-LOTO-1, ALPHA-PM-HP200-B, ALPHA-DIA-P100-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-HP-200 Hydraulic Press - Equipment Manual

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-MAN-HP200-B |
| Source identifier | AM-DOC-1042 |
| Equipment | ALPHA-HP-200 |
| Also covers | ALPHA-HP-200B (variant differences listed under Variant coverage) |
| Document type | Equipment manual |
| Revision | Rev B |
| Effective date | 2025-06-01 |
| Status | current |
| Supersedes | ALPHA-MAN-HP200-A |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-SAF-HP200-LOTO-1, ALPHA-PM-HP200-B, ALPHA-DIA-P100-1 |
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
   differences are listed under Variant coverage.

## Reason for this revision

Rev B was issued after the 2025 press structural survey and the reliability
review that followed it. The survey found two presses in the fleet with
tie-rod fretting and one post weld with an indication that was accepted after
re-inspection. The reliability review found two unplanned stoppages on this
press caused by oil contamination.

The engineering changes in Rev B are deliberately conservative: pressures are
lower, speeds near the tool are lower, and inspection and maintenance
intervals are shorter. Nothing in Rev B relaxes a limit.

## Equipment overview

The press is a four-post, single-ram unit fed from hydraulic power unit
ALPHA-P-100 (30 kW, fixed displacement pump, 63 l/min). The ram is located and
guided by four tie rods and four adjustable gib blocks; ram parallelism is
maintained by adjusting the gib blocks, not by the hydraulic system.

Tooling is supported on an upper bolster carried by the ram and a fixed lower
bolster. Both bolsters are T-slotted on 36 mm centres. Tool holding is by
bolster clamping screws; the press has no die cushion, so the tool and the
closed ram are left under full stored load whenever the ram is down. The
counterbalance cylinders hold the ram weight only while the pump motor is
energised.

## Technical data

| Parameter | Value |
| --- | --- |
| Rated press force at full daylight | 2000 kN |
| Relief valve set point (main circuit) | 210 bar |
| Maximum permissible working pressure | 205 bar |
| Hard-wired high pressure trip | 225 bar |
| Secondary (tool clamp) circuit set point | 180 bar |
| Rated capacity daylight | 1200 mm |
| Stroke | 800 mm |
| Die closing height | 120 mm minimum, 1100 mm maximum |
| Bed size | 1400 mm x 1200 mm, T-slots on 36 mm centres |
| Ram speed, approach | 60 mm/s |
| Ram speed, working | 25 mm/s |
| Ram speed, final 30 mm of stroke | 8 mm/s maximum |
| Ram speed at die entry, daylight above 1000 mm | 10 mm/s maximum |
| Motor | 30 kW, 400 V, three phase, 1460 rpm |
| Pump | fixed displacement, 63 l/min |
| Hydraulic oil | ISO VG 46 mineral, Alpha specification AM-H46 |
| Reservoir | 260 l, sight gauge plus high and low level switches |
| Return line filtration | 10 micron, element AM-FL-10 |
| Tie-rod nut torque | 340 N.m, re-torque every 2000 running hours |
| Tie-rod re-torque method | three passes in diagonal sequence, cross pattern |
| Die height sensor calibration | every 750 running hours |
| Hydraulic oil analysis | every 300 running hours, and after any hose burst |
| Ram parallelism | 0.5 mm maximum per metre of die face |
| Post weld inspection | every 3000 running hours, and after any overload event |
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
  900 ms; releasing either hand before 900 ms must not produce any ram motion.
- Safety-rated stop time, controls to ram stop: 250 ms maximum.
- Performance level of the two-hand control and the stop function: category 3,
  PL d, per the press safety circuit assessment.
- Upper ram stop switch and lower ram stop switch are independent of the
  die height sensor.
- Die height sensor: mechanical plunger type, part AM-DHS-22. It is a
  protective measure, not a positioning device.
- Counterbalance pressure must be present before the main relief opens. Loss
  of counterbalance with the ram down causes the ram to drop.
- The two-hand control must never be defeated, jumpered, tape bridged or
  overridden. Any diagnostic that requires defeating the safety circuit needs a
  documented risk assessment, a permit and a second authorised person present.

## Operating limits and permitted range

1. Working pressure must not exceed 205 bar at the manifold. The relief valve
   is set at 210 bar and is not adjustable in service. Any requirement to
   reduce pressure is raised as a work order for Maintenance Engineering.
   A reading above 205 bar with an empty die is a stop condition: stop the
   press, do not adjust the relief valve, and raise a work order.
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
   precision operation.
6. Any overload event, that is any event in which the hard-wired high
   pressure trip operated, is a structural inspection trigger. The press must
   not be returned to production until the post weld inspection in Technical data
   is complete.

## Variant coverage

ALPHA-HP-200B is an ALPHA-HP-200 retrofitted with the 300 mm extended ram kit
(kit AM-KIT-R300). If the asset plate on the press carries the suffix B, the
following values differ from Technical data and Variant coverage in this manual:

| Parameter | ALPHA-HP-200 | ALPHA-HP-200B |
| --- | --- | --- |
| Rated daylight | 1200 mm | 1500 mm |
| Stroke | 800 mm | 800 mm |
| Tie-rod nut torque | 340 N.m | 390 N.m |
| Tie-rod re-torque interval | 2000 running hours | 1500 running hours |
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

- Hydraulic oil analysis every 300 running hours, and after any hose burst.
- Tie-rod re-torque every 2000 running hours, three diagonal passes.
- Die height sensor calibration every 750 running hours.
- Ram parallelism check every 1000 running hours.
- Structural inspection of the four post welds every 3000 running hours, and
  after any overload event.
- Die entry speed reduction for tools with more than 1000 mm daylight.

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
- Accelerometer alarm thresholds used by the ram monitoring system: set in the
  condition monitoring configuration, not in this manual.
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

- Hydraulic pressure above 205 bar with no tooling load in the die.
- Audible knocking from the pump that does not stop when the relief opens.
- Visible hydraulic oil in the die area, on the tie rods or inside the frame.
- Ram side movement above 2 mm, or a parallelism reading outside 0.5 mm per
  metre.
- Any overload event in which the high pressure trip operated.
- Any broken wire, cracked bolster clamp or damaged guard discovered during an
  inspection.
- Repeated tripping of the safety circuit on the same cycle of the two-hand
  control.
- A required value is missing from the controlled document set.

Escalation route: Level 2 Maintenance Engineering, then the Production
Supervisor, then EHS for anything involving stored energy or structural
damage.

## Appendix: Revision B change impact assessment

Revision B changed three technical values and one inspection interval from
Revision A. This appendix records the impact of each change so that a
technician holding an older work order can see what must be re-checked.

| Change | Revision A | Revision B | Impact |
| --- | --- | --- | --- |
| Main relief set point | 240 bar | 210 bar | Reduce the setting and re-seal; retrain operators |
| Oil analysis interval | 500 running hours | 300 running hours | Update the PM schedule and the oil budget |
| Tie-rod re-torque interval | 4000 running hours | 2000 running hours | Update the PM schedule; re-torque at next stop |
| Accumulator pre-charge | 5 bar | 5 bar | No change |

The relief valve change is the significant one. A press that is still set to
240 bar after the revision takes effect will exceed the maximum permissible
working pressure of the circuit and is a stop condition. The setting is
verified at every annual service and after any relief valve work.

Work orders raised before the Revision B effective date remain valid until
they are worked; a work order that specifies a superseded value must be
reissued against Revision B before the work starts.

## Appendix: Operator daily and weekly checks

Daily and weekly checks are the first line of defence against a failure that
would otherwise be found only at a planned service. They are performed by the
operator and countersigned by the shift supervisor.

Daily checks before first start:

- Confirm the hydraulic oil level is between the low and high marks.
- Confirm the oil temperature is above 20 degC before working at full load.
- Confirm the guard and light curtain are in place and undamaged.
- Confirm the emergency stop is not latched and resets correctly.
- Confirm there is no oil on the floor or on the bolster.
- Confirm the pressure gauge reads zero with the pump stopped.

Weekly checks:

- Confirm the pressure gauge reading matches the controller at working
  pressure within 5 bar.
- Confirm the tie-rod nuts show no sign of movement by checking the witness
  marks.
- Confirm the gib adjustment bolts are tight and the ram moves without
  hesitation.
- Confirm the oil in the sight glass is clear and free of milky emulsion.
- Confirm the accumulator safety block is open and tagged.
- Confirm the pump and motor mounts are not loose by checking for movement.

Any check that fails is reported before the next shift. A failed safety check
stops the press until it is corrected and re-verified.

## Appendix: Torque and fastener reference

The values below apply to fasteners that are replaced or re-torqued during
maintenance of the ALPHA-HP-200 press. Torque is applied with a calibrated
torque wrench and the value is recorded on the work order. Lubricated threads
use the thread lubricant stated in the table; anti-seize paste is not used on
fasteners in the hydraulic circuit.

| Fastener | Size and thread | Grade | Torque | Thread condition |
| --- | --- | --- | --- | --- |
| Frame tie-rod nut | M42 x 4.5 | 10.9 | 340 N.m | dry, three diagonal passes |
| Crown and base bolt | M24 x 3 | 10.9 | 780 N.m | dry |
| Column foot bolt | M30 x 3.5 | 8.8 | 610 N.m | dry |
| Ram guide shoe bolt | M16 x 2 | 8.8 | 190 N.m | dry |
| Relief valve cartridge | M20 x 1.5 | 8.8 | 60 N.m | hydraulic oil film |
| Accumulator flange bolt | M24 x 3 | 10.9 | 320 N.m | hydraulic oil film |
| Pump mounting bolt | M12 x 1.75 | 8.8 | 85 N.m | dry |
| Manifold subplate bolt | M10 x 1.5 | 12.9 | 55 N.m | dry |
| Guard panel bolt | M8 x 1.25 | 8.8 | 24 N.m | dry |
| Two-hand control bracket bolt | M6 x 1 | 8.8 | 10 N.m | dry |

Fasteners removed from a safety device are replaced, not reused. Frame
fasteners are reused only if the threads are undamaged and the shank is not
corroded; otherwise they are replaced with a fastener of the same grade. A
fastener that has been torqued past its yield, identified by a stretched shank
or a nut that turns freely after it has seated, is scrapped and the reason is
recorded.

Torque sequence for the four tie-rods is diagonal and is repeated in three
passes: a first pass at one third of the final value, a second pass at two
thirds, and a final pass at the full value. The re-torque interval is the one
stated in the technical data table of the current revision of this manual.

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
  during forming; the ALPHA-HP-200 does not have one.
- Hold-to-run: a control principle in which the motion continues only while
  the operator holds the command device.
- Lift-off pressure: the pressure at which a relief valve first opens and
  passes a measurable flow.
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
- Two-hand control: a control circuit that requires both hands on separate
  buttons within a short time window before a hazardous motion can start.
- Zero-energy verification tag: the tag fitted after isolation and
  verification to record that the asset is in a de-energised and proven state.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev A | 2023-03-01 | First controlled issue for ALPHA-HP-200 after the 2023 press rebuild. |
| Rev B | 2025-06-01 | Structural survey and reliability review. Reduced pressure limits and approach speeds, added post weld inspection and tightened maintenance intervals. |
