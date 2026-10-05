---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-LUB-CNC3X-1"
source_id: "AM-DOC-1155"
title: "ALPHA-CNC-3X Machining Centre - Lubrication Schedule"
equipment: "ALPHA-CNC-3X"
equipment_also_covers: "none; the CNC-3XL linear rail variant is out of scope, see Documentation gaps"
document_type: "lubrication-schedule"
document_type_name: "Lubrication schedule"
revision: "Rev 1"
effective_date: "2024-01-15"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "AM-MAN-CNC3X-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-CNC-3X Machining Centre - Lubrication Schedule

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-LUB-CNC3X-1 |
| Source identifier | AM-DOC-1155 |
| Equipment | ALPHA-CNC-3X |
| Also covers | none; the CNC-3XL linear rail variant is out of scope, see Documentation gaps |
| Document type | Lubrication schedule |
| Revision | Rev 1 |
| Effective date | 2024-01-15 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | AM-MAN-CNC3X-1 |
| Document owner | Maintenance Engineering |

## Purpose

This schedule defines the lubricants, quantities and intervals for the
ALPHA-CNC-3X three axis machining centre in Bay 2. It covers the way
lubrication system, the spindle lubrication system and the manual greasing
points.

Using the wrong lubricant on this machine voids the spindle warranty and can
scratch the guideways within one shift.

## Lubricants

| Application | Specification | Grade | Colour |
| --- | --- | --- | --- |
| Way lubrication, central system | Alpha specification AM-WL68 | ISO VG 68 | amber |
| Spindle lubrication, oil | Alpha specification AM-SL40 | ISO VG 40 | light amber |
| Spindle bearing grease, re-greasing | Alpha specification AM-G2 | NLGI 2 lithium complex | white to off white |
| Way guide grease, manual points only | Alpha specification AM-G2 | NLGI 2 lithium complex | white to off white |

AM-G2 is the only approved grease on this machine. Do not use a polyurea, a
complex or a high temperature grease on the spindle bearings. Do not use a
grease labelled for a linear guideway in the way lubrication system, which is
an oil system.

## Safety prerequisites

1. Never lubricate with the spindle running. Lock the spindle in the
  orientation selected in the lock function and confirm the lock is active
  from the control panel before opening the enclosure.
2. After a power failure or an emergency stop, the spindle coasts down for up
  to 4 minutes. Do not open the enclosure until the spindle has been at rest
  for 5 minutes, and confirm it by observing the spindle through the window.
3. Never put a hand or a tool into the tool magazine while the magazine is
  indexing, and never while the magazine door is open.
4. The coolant tank is pressurised by a pump. Depressurise before opening the
  tank lid.
5. Swarf is sharp. Use gloves and eye protection for any manual greasing point
  inside the enclosure.

## Way lubrication system

Central oil system, one tank, one pump and one distribution manifold.

| Task | Interval | Criterion |
| --- | --- | --- |
| Oil level check at the tank sight glass | Daily | Between the marks |
| Observe the pressure indicator during a cycle | Daily | Flag clear for the whole cycle |
| Top up with AM-WL68 | As required | Quantity to bring level between the marks |
| Clean the chip auger and the coolant filter | Every 250 running hours | No chips carried into the coolant |
| Sample the way oil for viscosity | Every 1000 running hours | Plus or minus 10 percent of ISO VG 68 |

A pressure indicator that stays set during a cycle means a blocked
distribution pipe or a failed pump. Run the machine down at the first safe
opportunity: starved way lubrication damages the guideways within hours.

## Spindle lubrication

Oil system, ISO VG 40, with a separate reservoir and a pressure switch.

| Task | Interval | Criterion |
| --- | --- | --- |
| Oil level | Weekly | Between the marks |
| Oil temperature at the spindle return | Each shift | 30 degC to 45 degC at 6000 rpm |
| Oil sample for analysis | Every 1000 running hours | ISO 4406 18/16/13 or cleaner, water below 0.05 percent |
| Spindle bearing re-greasing | Every 2000 running hours | Quantity under Spindle bearing re-greasing |

Spindle oil temperature above 45 degC at rated speed requires the bearing
temperature to be read from the control panel. Spindle bearing temperature
above 70 degC at rated speed is a stop condition for the spindle.

## Spindle bearing re-greasing

Interval: every 2000 running hours, or every 500 running hours if the spindle
is used continuously above 8000 rpm.

1. Confirm the spindle is locked and at rest for at least 5 minutes.
2. Remove the spindle nose cover as described in the machine manual.
3. Take the used grease out of the bearing housing with a grease gun fitted
   with a cleaning adapter. Do not leave mixed grease in the housing.
4. Add AM-G2 in the quantity below, in three strokes, with the spindle nose
   pointing up so the grease enters the upper bearing first.
5. Turn the spindle by hand through one full revolution after each stroke.
6. Replace the nose cover, confirm the spindle runs at rated speed with no
   noise increase, and record the quantity used.

Quantity per re-greasing:

| Spindle bearing | AM-G2 quantity |
| --- | --- |
| Front upper and lower | 3 g each |
| Rear upper and lower | 3 g each |
| Angular contact pair per side | 6 g |

Over-greasing the spindle bearings is a real failure mode on this machine
type: excess grease heats the bearing and shortens its life. Do not exceed the
quantities above.

The re-greasing interval for the CNC-3XL variant spindle is different and is
in the linear rail variant manual, which is not in this document collection.
Check the asset plate before starting this task.

## Tool change and coolant

| Task | Interval | Criterion |
| --- | --- | --- |
| Tool life check on the tool list | Every shift | No tool running past its life |
| Coolant concentration | Weekly | 6 to 9 percent, refractometer only |
| Coolant pH | Weekly | 8.5 to 9.5 |
| Coolant tank and chip conveyor clean | Every 500 running hours | No tramp oil, no visible bacteria |
| Spindle nose and tool holder clean | Every 500 running hours | No chip packing in the taper |

Never use the concentration float on the tank. Use a refractometer. The float
gives false readings in the range 6 to 9 percent, which is exactly the working
range.

Tool life on this machine is expressed as cutting minutes per tool. A tool past
its life limit that breaks in the spindle is a reportable incident.

## Documentation gaps

Not contained in this schedule:

- The ball screw pre-load setting for the X, Y and Z axes. These are set at
  installation and are recorded on commissioning sheet CM-CNC3X-01, which is
  not in this document collection. The pre-load is not adjusted in routine
  lubrication work. If a pre-load value is needed for an investigation, raise
  a documentation request and read the commissioning sheet; do not measure
  and substitute a value.
- The backlash acceptance limit at table reversal. There is no figure for it
  in this schedule and none may be inferred from it.
- The guideway wipe and gib adjustment intervals, which are in the machine
  manual preventive section.
- The lubricant intervals for the CNC-3XL linear rail variant, whose guideways
  are grease lubricated rather than oil lubricated and whose quantities are
  different.

## Appendix: Lubricant cross reference and application points

The machine uses several lubricants and each application point must receive
the correct product. Mixing products or substituting a product without
approval damages the machine and voids the warranty.

| Application point | Product | Quantity | Interval | Method |
| --- | --- | --- | --- | --- |
| Way lubrication, X axis | ISO VG 68 way oil | 2.5 l | Automatic, reservoir check weekly | Pump |
| Way lubrication, Y axis | ISO VG 68 way oil | 2.0 l | Automatic, reservoir check weekly | Pump |
| Way lubrication, Z axis | ISO VG 68 way oil | 2.5 l | Automatic, reservoir check weekly | Pump |
| Ball screw, X axis | Grease X, NLGI 2 | 5 g | Every 2000 hours | Grease gun |
| Ball screw, Y axis | Grease X, NLGI 2 | 5 g | Every 2000 hours | Grease gun |
| Ball screw, Z axis | Grease X, NLGI 2 | 5 g | Every 2000 hours | Grease gun |
| Spindle cartridge | Spindle grease | As service kit | On replacement | Service |
| Tool magazine | Grease X, NLGI 2 | 10 g | Every 1000 hours | Grease gun |
| Chuck grease nipple | Chuck grease | 3 g | Weekly | Grease gun |
| Tailstock | ISO VG 68 way oil | 0.5 l | Monthly | Oil can |

The reservoir is checked weekly and topped up with the correct product. A
reservoir that empties faster than expected is a fault and is investigated
before the machine is run unattended.

## Appendix: Lubrication fault symptoms and causes

Lubrication faults rarely appear as lubrication faults. They appear as
accuracy drift, surface finish problems or premature component wear. The table
maps the symptom to the lubrication cause.

| Symptom | Likely lubrication cause | Check |
| --- | --- | --- |
| Poor surface finish on one axis | Low way oil or blocked metering unit | Reservoir level and metering unit output |
| Axis position drift | Contaminated way oil or worn slide | Oil condition and slide clearance |
| Spindle noise | Spindle grease exhausted | Spindle service history |
| Ball screw noise | Dry ball screw | Grease at the nut |
| Chuck will not hold | Chuck grease insufficient | Grease nipple and chuck operation |
| Oil on the floor | Over-lubrication or blocked return | Metering unit setting and return line |
| Overheat alarm on an axis | Wrong way oil viscosity | Product in the reservoir |

A lubrication fault is confirmed by finding the physical cause, not by adding
more lubricant. Adding lubricant to a blocked system does not reach the slide
and may cause a slip hazard.

## Appendix: Lubricant, coolant and grease reference

| Application | Specification | Capacity | Interval |
| --- | --- | --- | --- |
| Way lubrication | ISO VG 68, AM-W68 | 6 l reservoir | top up weekly, change annually |
| Spindle lubrication | grease, AM-S2 | sealed for life | at 12000 running hours |
| Ball-screw lubrication | grease, AM-B2 | 30 g per screw | every 2000 running hours |
| Linear guide grease | grease, AM-L2 | 12 g per block | every 2000 running hours |
| Tool changer cam | grease, AM-C1 | 20 g | every 3000 running hours |
| Coolant | water miscible, 6 to 8 percent | 200 l tank | measure weekly, change every 3000 hours |
| Hydraulic chuck oil | ISO VG 32 | 4 l | every 4000 running hours |
| Automatic greaser cartridge | AM-G4 | 1 | when the low-level alarm shows |

Coolant concentration is measured with a refractometer at the tank and at the
return line. A concentration below 5 percent is corrected before the next
shift. Tramp oil is skimmed weekly. Coolant that has a strong smell, a pH below
8.5 or visible swarf build-up is changed rather than topped up.

Grease fittings are wiped clean before the grease gun is attached so that grit
is not pushed into the bearing. The automatic greaser is refilled with the
cartridge stated in the table; a substitute cartridge is a non-conformance.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2024-01-15 | First controlled issue, aligned with the machine manual issued 2023. |
