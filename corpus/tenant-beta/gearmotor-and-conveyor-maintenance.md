---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-PM-CV200-1"
source_id: "BM-DOC-2318"
title: "BETA-CV-200 Belt Conveyor and Gearmotor - Maintenance Procedure"
equipment: "BETA-CV-200"
equipment_also_covers: "BETA-GM-45 gearmotor (BETA-GM-45S differences listed under Section 7: gearmotor variants)"
document_type: "maintenance-procedure"
document_type_name: "Preventive maintenance procedure"
revision: "Rev 1"
effective_date: "2024-04-01"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BM-MAN-CV200-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-CV-200 Belt Conveyor and Gearmotor - Maintenance Procedure

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-PM-CV200-1 |
| Source identifier | BM-DOC-2318 |
| Equipment | BETA-CV-200 |
| Also covers | BETA-GM-45 gearmotor (BETA-GM-45S differences listed under Section 7: gearmotor variants) |
| Document type | Preventive maintenance procedure |
| Revision | Rev 1 |
| Effective date | 2024-04-01 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | BM-MAN-CV200-1 |
| Document owner | Maintenance Engineering |

## Purpose

This procedure covers the belt conveyor BETA-CV-200, which carries machined
parts from the Line 1 machining cell to the wash bay, and the gearmotor that
drives it.

The conveyor has a gravity loaded take-up on the 100 ft section. That stored
energy is the main hazard on this machine.

## Technical data

| Parameter | Value |
| --- | --- |
| Belt width | 30 in |
| Belt | 3/4 in, 3 ply, 400 lb/in |
| Belt speed | 150 ft/min |
| Conveyor length | 500 ft, fixed take-up on the first 300 ft, gravity counterweight on the 100 ft section |
| Drive | BETA-GM-45 gearmotor, i = 30, output 50 rpm, 4.0 hp |
| Maximum belt tension | 100 lb per in of belt width |
| Belt sag at mid span, tensioned | 2 percent of the span |
| Belt tracking acceptance | plus or minus 0.25 in at the tail pulley |
| Idler rollers | 3.5 in diameter, three roll troughing idlers |
| Take-up travel | 16 in, counterweighted on the 100 ft section |

Belt tension is measured with a tension gauge at the marked measuring points on
the frame. A sag figure from another conveyor is not a tension figure.

## Energy isolation for this conveyor

Before any work on the conveyor, the gearmotor or the belt:

1. Stop the conveyor from the local stop button and set the selector to off.
2. Isolate the drive at panel MCC-7 breaker 9, locked and tagged.
3. Lock the take-up. On the counterweighted section, fit the counterweight
   clamp BM-2210 over the weight guide and fit the take-up pin BM-2215 through
   the take-up bracket. The counterweight clamp must be fitted before the pin,
   and the pin is not removed until the conveyor has been run unloaded.
4. Isolate the auxiliary 24 V supply to the belt speed switch at MCC-7 breaker
   15.
5. Verify zero energy: attempt start from the local button and from the remote
   station, confirm no movement, confirm the belt cannot be moved by hand at
   the head pulley.
6. Fit the lock box if more than one person works on the conveyor.

Removing a guard, clearing a jam or working near the nip points requires this
isolation. A jam at the head pulley nip is cleared with a rod and a lockout,
never with hands and never with the belt drive in auto.

## Belt tensioning and tracking

Tracking:

1. Run the conveyor unloaded at reduced speed, about 60 ft/min, from the local
   station, with the area clear.
2. Observe the tail pulley. Adjust the tail pulley take-up screws in 0.08 in
   increments at whichever end needs correction.
3. Never adjust both screws on one end at the same time.
4. Criterion: the belt runs centred, within plus or minus 0.25 in at the tail
   pulley, with no edge wear after 20 minutes of running.

Tension, fixed section:

- Target sag 2 percent of the span at the marked measuring points, using a
  tension gauge.
- Adjust the screw take-up in 0.4 in increments, never more than 4 in in one
  adjustment.
- If the screw take-up reaches the end of its travel, the belt is too short or
  the take-up has been set wrong. Do not shorten the belt to compensate. Raise
  a work order.

Counterweighted take-up:

- If the counterweight must be adjusted, fit the clamp and the pin first,
  adjust in 1 in increments, then run the conveyor unloaded before removing
  the pin.
- The counterweight mass and the permitted travel are on the installation
  record, which is not part of this document collection.

## Gearmotor maintenance

| Task | Interval | Criterion |
| --- | --- | --- |
| Oil level check at the sight glass | Weekly | Between the marks |
| Oil temperature at the gearbox during a loaded run | Each shift | Below 158 degF |
| Listen for bearing whine | Each shift | No whine that rises with load |
| Oil change | Every 6000 running hours | To the mark after a warm running period |
| Oil analysis | Every 6000 running hours | No metal content above the limit, water below 0.05 percent |
| Breather clean | Every 2000 running hours | Breather clear |
| Base bolt torque check | Every 6000 running hours | To the value on the foundation drawing |

The foundation drawing is not part of this document collection. If the base
bolt torque value is not available, do not retighten the base bolts; check for
movement of the base instead and raise a documentation request.

Oil type for the gearmotor is stated on the gearbox nameplate and on the gear
oil data sheet. The gear oil data sheet is not part of this document
collection. Do not fill from a neighbouring machine.

## Belt and pulleys

| Task | Interval | Criterion |
| --- | --- | --- |
| Belt edge wear inspection | Weekly | No edge wear more than 0.12 in |
| Belt splice inspection | Weekly | Splice intact, no edge lifting |
| Head pulley lagging inspection | Monthly | No wear more than 0.20 in, no glazing |
| Pulley and idler bearing noise | Weekly | No noise, no flat spots on the belt face |
| Idler rotation check, all rollers | Quarterly | Every roller turns freely |
| Head and tail pulley bearing temperature | Weekly | Below 140 degF |

Replacement criteria:

- Replace the belt when the carcass shows exposed plies, when a splice shows
  more than one broken ply, or when the belt is more than 36 months old.
- Replace the head pulley lagging when the wear limit above is reached or when
  the lagging thickness is below 0.25 in.
- Replace rollers that do not turn freely, that show a flat spot or a failed
  seal.

## Section 7: gearmotor variants

| Parameter | BETA-GM-45 | BETA-GM-45S high torque |
| --- | --- | --- |
| Rated power | 4.0 hp | 5.0 hp |
| Gear ratio | 30 | 40 |
| Output speed | 50 rpm | 39 rpm |
| Oil quantity | 2.2 l | 3.1 l |
| Output torque | 760 N.m | 1140 N.m |
| Fitted to | BETA-CV-200, 100 ft section | BETA-CV-200, head end drive |

The two gearmotors use different oil quantities and different ratios. Fitting
a GM-45S nameplate value to a GM-45, or the other way round, causes either a
starved gearbox or an overfilled one. Read the nameplate on the gearbox.

## Documentation gaps

Not contained in this procedure:

- The gear oil specification and the base bolt torque values.
- The counterweight mass and the permitted take-up travel on the
  counterweighted section, which are on the installation record.
- The belt splice procedure and the vulcanising equipment specification.
- The speed switch calibration value for the belt speed measurement.
- The anti-slip backstop specification for the inclined section.

## Appendix: Component replacement intervals and evidence

The conveyor and gearmotor are maintained on a combination of running hours
and condition. The table gives the planned intervals and the evidence required
to close each task.

| Component | Interval | Acceptance criterion | Evidence |
| --- | --- | --- | --- |
| Gearmotor lubricant | 5000 h or 12 months | Correct grade and level | Product and volume |
| Gearmotor breather | 2000 h | Clean and clear | Part number |
| Belt tracking | Weekly | Belt centred within 0.4 in | Photograph |
| Belt tension | Monthly | Within the deflection limit | Measured deflection |
| Belt condition | Monthly | No splits, no exposed plies | Photograph |
| Roller bearings | 4000 h | Free rotation, no noise | Grease record |
| Pulley lagging | 12 months | No separation, adequate grip | Inspection record |
| Scraper | Monthly | Contacts the belt evenly | Photograph |
| Guarding | Monthly | Present and secure | Inspection record |
| Emergency stop | Monthly | Stops the conveyor | Test record |

A belt at the end of its adjustment or with exposed plies is replaced. A
gearmotor that is noisy or hot is removed from service and inspected before it
fails and damages the belt.

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
| Rev 1 | 2024-04-01 | First controlled issue. |
