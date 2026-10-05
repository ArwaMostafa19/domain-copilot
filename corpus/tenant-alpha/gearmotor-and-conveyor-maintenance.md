---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-PM-CV200-1"
source_id: "AM-DOC-1170"
title: "ALPHA-CV-200 Belt Conveyor and Gearmotor - Maintenance Procedure"
equipment: "ALPHA-CV-200"
equipment_also_covers: "ALPHA-GM-45 gearmotor (ALPHA-GM-45S differences listed under Section 7: gearmotor variants)"
document_type: "maintenance-procedure"
document_type_name: "Preventive maintenance procedure"
revision: "Rev 1"
effective_date: "2024-03-12"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "AM-MAN-CV200-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-CV-200 Belt Conveyor and Gearmotor - Maintenance Procedure

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-PM-CV200-1 |
| Source identifier | AM-DOC-1170 |
| Equipment | ALPHA-CV-200 |
| Also covers | ALPHA-GM-45 gearmotor (ALPHA-GM-45S differences listed under Section 7: gearmotor variants) |
| Document type | Preventive maintenance procedure |
| Revision | Rev 1 |
| Effective date | 2024-03-12 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | AM-MAN-CV200-1 |
| Document owner | Maintenance Engineering |

## Purpose

This procedure covers the belt conveyor ALPHA-CV-200, which carries pressed
parts from the ALPHA-HP-200 press to the shot blast cell, and the gearmotor
that drives it.

The conveyor runs under a gravity loaded idler frame and has a counterweighted
take-up. That stored energy is the main hazard on this machine.

## Technical data

| Parameter | Value |
| --- | --- |
| Belt width | 750 mm |
| Belt | 18 mm, 2 ply, 400 N/mm |
| Belt speed | 0.75 m/s |
| Conveyor length | 200 m, fixed and screw take-up on 60 m section |
| Drive | ALPHA-GM-45 gearmotor, i = 25, output 63 rpm, 3.0 kW |
| Maximum belt tension | 60 N/mm of belt width |
| Belt sag at mid span, tensioned | 1.5 percent of the span |
| Belt tracking acceptance | plus or minus 5 mm at the tail pulley |
| Idler rollers | 89 mm diameter, 3 roll troughing idlers, self cleaning |
| Take-up travel | 400 mm, counterweighted on the 60 m section |

Belt tension is measured with a tension gauge at the marked measuring points
on the frame. A sag figure from another conveyor is not a tension figure.

## Safety prerequisites

Before any work on the conveyor, the gearmotor or the belt:

1. Stop the conveyor from the local stop button and set the selector to off.
2. Isolate the drive at panel MCC-7 breaker 5, locked and tagged.
3. Lock the take-up: fit the take-up lock pin AM-9855 through the take-up
   bracket, or lock the counterweight block in place with the supplied
   clamp. This is required because the take-up is gravity loaded and the belt
   is always under tension.
4. Isolate the auxiliary 24 V supply to the belt speed switch at MCC-7 breaker
   11.
5. Verify zero energy: attempt start from both the local button and the
   remote station, confirm no movement, confirm the belt cannot be moved by
   hand at the head pulley.
6. Fit the lock box if more than one person works on the conveyor.

Removing a guard, clearing a jam or working near the nip points requires this
isolation. A jam at the head pulley nip is cleared with a rod and a lockout,
never with hands and never with the belt drive in auto.

## Belt tensioning and tracking

Tracking, 200 m conveyor:

1. Run the conveyor unloaded at reduced speed, about 0.25 m/s, from the local
   station, with the area clear.
2. Observe the tail pulley. Adjust the tail pulley take-up screws in 2 mm
   increments at whichever end needs correction.
3. Never adjust both screws on one end at the same time. Two adjustments at
   one end is a common cause of a belt that tracks to one side permanently.
4. Criterion: the belt runs centred, within plus or minus 5 mm at the tail
   pulley, and there is no edge wear after 20 minutes of running.

Tension, fixed section:

- Target sag 1.5 percent of the span at the marked measuring points, using a
  tension gauge.
- Adjust the screw take-up on the 60 m section only in 10 mm increments, and
  never more than 100 mm in one adjustment.
- If the screw take-up reaches the end of its travel, the belt is too short or
  the take-up has been set wrong. Do not shorten the belt to compensate. Raise
  a work order.

Counterweighted take-up:

- If the counterweight must be adjusted, fit the lock pin first, adjust in
  25 mm increments, then remove the pin and run the conveyor unloaded.
- Do not leave the counterweight unsecured. The pin installation procedure is
  not described in this document collection; the safe working rule is that the
  counterweight block is clamped in place before any adjustment and is not
  released until the conveyor has been run unloaded.

## Gearmotor maintenance

| Task | Interval | Criterion |
| --- | --- | --- |
| Oil level check at the sight glass | Weekly | Between the marks |
| Oil temperature at the gearbox during a loaded run | Each shift | Below 70 degC |
| Listen for bearing whine | Each shift | No whine that rises with load |
| Oil change | Every 6000 running hours | Gearbox oil level to the mark after the warm running period |
| Oil analysis | Every 6000 running hours | No metal content above the limit, water below 0.05 percent |
| Breather clean | Every 2000 running hours | Breather clear |
| Base bolt torque check | Every 6000 running hours | To the value on the foundation drawing |

The foundation drawing is not part of this document collection. If the base bolt
torque value is not available, do not retighten the base bolts; check for
movement of the base instead and raise a documentation request.

Oil type for the gearmotor is stated on the gearbox nameplate and on the gear
oil data sheet. The gear oil data sheet is not part of this document
collection. Do not fill from a neighbouring machine.

## Belt and pulleys

| Task | Interval | Criterion |
| --- | --- | --- |
| Belt edge wear inspection | Weekly | No edge wear more than 3 mm |
| Belt splice inspection | Weekly | Splice intact, no edge lifting |
| Head pulley lagging inspection | Monthly | No wear more than 5 mm, no glazing |
| Pulley and idler bearing noise | Weekly | No noise, no flat spots on the belt face |
| Idler rotation check, all rollers | Quarterly | Every roller turns freely |
| Head and tail pulley bearing temperature | Weekly | Below 60 degC |

Replacement criteria:

- Replace the belt when the carcass shows exposed plies, when a splice shows
  more than one broken ply, or when the belt is more than 36 months old.
- Replace the head pulley lagging when the wear limit above is reached or when
  the lagging thickness is below 6 mm.
- Replace rollers that do not turn freely, that show a flat spot or a failed
  seal.

## Section 7: gearmotor variants

| Parameter | ALPHA-GM-45 | ALPHA-GM-45S high torque |
| --- | --- | --- |
| Rated power | 3.0 kW | 4.5 kW |
| Gear ratio | 25 | 40 |
| Output speed | 63 rpm | 39 rpm |
| Oil quantity | 1.8 l | 2.6 l |
| Output torque | 460 N.m | 1140 N.m |
| Fitted to | ALPHA-CV-200, 60 m section | ALPHA-CV-200, head end drive |

The two gearmotors use different oil quantities and different ratios. Fitting
a GM-45S nameplate value to a GM-45, or the other way round, causes either a
starved gearbox or an overfilled one. Read the nameplate on the gearbox.

A CV-200 with a GM-45S at the head end and a GM-45 on the 60 m section is
correct. A CV-200 with a GM-45 at the head end that will not move its load is
not a pulley or belt fault; compare the nameplate first.

## Documentation gaps

Not contained in this procedure:

- The gear oil specification and the base bolt torque values.
- The take-up lock pin installation and proof test procedure, AM-PM-CV200-LOCK.
- The belt splice procedure and the vulcanising equipment specification.
- The counterweight mass and the permitted take-up travel on the
  counterweighted section, which are on the installation record.
- The speed switch calibration value for the belt speed measurement.

## Appendix: Component replacement intervals and evidence

The conveyor and gearmotor are maintained on a combination of running hours
and condition. The table gives the planned intervals and the evidence required
to close each task.

| Component | Interval | Acceptance criterion | Evidence |
| --- | --- | --- | --- |
| Gearmotor lubricant | 6000 h or 12 months | Correct grade and level | Product and volume |
| Gearmotor breather | 2000 h | Clean and clear | Part number |
| Belt tracking | Weekly | Belt centred within 5 mm | Photograph |
| Belt tension | Monthly | Within the deflection limit | Measured deflection |
| Belt condition | Monthly | No splits, no exposed plies | Photograph |
| Roller bearings | 4000 h | Free rotation, no noise | Grease record |
| Pulley lagging | 12 months | No separation, adequate grip | Inspection record |
| Scraper | Monthly | Contacts the belt evenly | Photograph |
| Guarding | Monthly | Present and secure | Inspection record |
| Emergency stop | Monthly | Stops the conveyor | Test record |

A belt that is at the end of its adjustment or that shows exposed plies is
replaced. A gearmotor that is noisy or hot is removed from service and
inspected before it fails and damages the belt.

## Appendix: Gearmotor fault diagnosis

Gearmotor faults usually appear as noise, heat, vibration or loss of drive.
The table maps the symptom to the checks and the likely cause.

| Symptom | Check | Likely cause |
| --- | --- | --- |
| Whining noise | Oil level and condition | Low or degraded oil |
| Knocking noise | Coupling alignment and key | Worn key or misalignment |
| Overheating | Load, oil, cooling fins | Overload or low oil |
| Vibration | Mounting bolts and foundation | Loose mounting |
| Oil leak at the output | Seal condition | Worn output seal |
| Oil leak at the breather | Oil level and breather | Overfilled or blocked breather |
| Loss of drive | Key, coupling and shear pin | Sheared key or failed coupling |
| Motor trips on start | Supply and mechanical load | Jammed conveyor or supply fault |

A gearmotor that is hot to the touch is stopped and allowed to cool before it
is inspected. Oil is drained and examined for metal particles; a gearmotor
with metal in the oil is overhauled, not topped up.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2024-03-12 | First controlled issue, after the 2023 counterweight incident review. |
