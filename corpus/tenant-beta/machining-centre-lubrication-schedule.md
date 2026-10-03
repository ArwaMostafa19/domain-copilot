---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-LUB-CNC3X-1"
source_id: "BM-DOC-2305"
title: "BETA-CNC-3X Machining Centre - Lubrication Schedule"
equipment: "BETA-CNC-3X"
equipment_also_covers: "none; the CNC-3XL linear rail variant is out of scope, see Documentation gaps"
document_type: "lubrication-schedule"
document_type_name: "Lubrication schedule"
revision: "Rev 1"
effective_date: "2024-02-26"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BM-MAN-CNC3X-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-CNC-3X Machining Centre - Lubrication Schedule

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-LUB-CNC3X-1 |
| Source identifier | BM-DOC-2305 |
| Equipment | BETA-CNC-3X |
| Also covers | none; the CNC-3XL linear rail variant is out of scope, see Documentation gaps |
| Document type | Lubrication schedule |
| Revision | Rev 1 |
| Effective date | 2024-02-26 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | BM-MAN-CNC3X-1 |
| Document owner | Maintenance Engineering |

## Purpose

This schedule defines the lubricants, quantities and intervals for the
BETA-CNC-3X three axis machining centre in the Line 1 machining cell. It
covers the central way lubrication system, the spindle lubrication system, the
manual greasing points and the tool change system.

Using the wrong lubricant on this machine voids the spindle warranty.

## Lubricants

| Application | Specification | Grade | Colour |
| --- | --- | --- | --- |
| Way lubrication, central system | Beta specification BM-WL46 | ISO VG 46 | amber |
| Spindle lubrication, oil | Beta specification BM-SL40 | ISO VG 40 | light amber |
| Spindle bearing grease, re-greasing | Beta specification BG-2 | NLGI 2 lithium complex | white to off white |
| Way guide grease, manual points only | Beta specification BG-2 | NLGI 2 lithium complex | white to off white |

BG-2 is the only approved grease on this machine. Do not use a polyurea, a
complex or a high temperature grease on the spindle bearings. The way
lubrication system on this machine takes oil, not grease; a grease-lubricated
guideway is a different machine variant whose data is not in this schedule, see
Documentation gaps.

## Safety prerequisites

- Never lubricate with the spindle running. Lock the spindle from the control
  panel and confirm the lock is active before opening the enclosure.
- After a power failure or an emergency stop the spindle coasts down for up to
  6 minutes on this machine. Do not open the enclosure until the spindle has
  been at rest for 8 minutes, confirmed through the window.
- Never put a hand or a tool into the side magazine while it is indexing, and
  never while the magazine door is open.
- The coolant tank is pressurised by a pump. Depressurise before opening the
  tank lid.
- Swarf is sharp. Gloves and eye protection for any manual greasing point.

## Way lubrication system

Central oil system, one tank, one pump, one distribution manifold.

| Task | Interval | Criterion |
| --- | --- | --- |
| Oil level check at the tank sight glass | Daily | Between the marks |
| Observe the pressure indicator during a cycle | Daily | Flag clear for the whole cycle |
| Top up with BM-WL46 | As required | To bring the level between the marks |
| Clean the chip conveyor and the coolant filter | Every 250 running hours | No chips carried into the coolant |
| Sample the way oil for viscosity | Every 1000 running hours | Plus or minus 10 percent of ISO VG 46 |

A pressure indicator that stays set during a cycle means a blocked
distribution pipe or a failed pump. Run the machine down at the first safe
opportunity: starved way lubrication damages the guideways within hours.

## Spindle lubrication

| Task | Interval | Criterion |
| --- | --- | --- |
| Oil level | Weekly | Between the marks |
| Oil temperature at the spindle return | Each shift | 75 degF to 105 degF at 6000 rpm |
| Oil sample for analysis | Every 1000 running hours | ISO 4406 18/16/13 or cleaner, water below 0.05 percent |
| Spindle bearing re-greasing | Every 3000 running hours | Quantity under Spindle bearing re-greasing |

Spindle oil temperature above 105 degF at rated speed requires the spindle
bearing temperature to be read from the control panel. A spindle bearing
temperature above 160 degF at rated speed is a stop condition for the spindle.

## Spindle bearing re-greasing

Interval: every 3000 running hours, or every 750 running hours if the spindle
is used continuously above 8000 rpm.

1. Confirm the spindle is locked and at rest for at least 8 minutes.
2. Remove the spindle nose cover as described in the machine manual.
3. Take the used grease out of the housing with a grease gun fitted with a
   cleaning adapter. Do not leave mixed grease in the housing.
4. Add BG-2 in the quantity below, in three strokes, with the spindle nose
   pointing up so the grease enters the upper bearing first.
5. Turn the spindle by hand through one full revolution after each stroke.
6. Replace the nose cover, confirm the spindle runs at rated speed with no
   noise increase, and record the quantity used.

| Spindle bearing | BG-2 quantity |
| --- | --- |
| Front upper and lower | 2 g each |
| Rear upper and lower | 2 g each |
| Angular contact pair per side | 4 g |

Over-greasing is a real failure mode: excess grease heats the bearing and
shortens its life. Do not exceed the quantities above.

The re-greasing interval for the CNC-3XL variant spindle is different and is
in the linear rail variant manual, which is not in this document collection.
Check the asset plate before starting this task.

## Tool change and coolant

| Task | Interval | Criterion |
| --- | --- | --- |
| Tool life check on the tool list | Every shift | No tool running past its life |
| Coolant concentration | Weekly | 7 to 10 percent, refractometer only |
| Coolant pH | Weekly | 8.5 to 9.5 |
| Coolant tank and chip conveyor clean | Every 500 running hours | No tramp oil, no visible bacteria |
| Side magazine chain tension check | Every 500 running hours | Within the manufacturer figure, chain not rusted |
| Spindle nose and tool holder clean | Every 500 running hours | No chip packing in the taper |

Never use the concentration float on the tank. Use a refractometer. The float
gives false readings in the range 7 to 10 percent, which is exactly the working
range.

Tool life on this machine is expressed as cutting minutes per tool, and a tool
past its life limit that breaks in the spindle is a reportable incident.

## Guideway backlash verification

This machine has a specified backlash acceptance, verified monthly and after
any collision:

- Indicator set in the table T-slot, at the centre of travel on each axis.
- Command the axis in one direction, stop, and read the indicator.
- Command the axis in the reverse direction, stop, and read the indicator.
- Acceptance: the difference between the two readings is 0.03 mm (0.0012 in) or
  less on each axis.

A reading outside the acceptance means the ballscrew pre-load or the gib is
worn. Do not adjust the gib as a lubricant task; raise a work order for
Maintenance Engineering. The ballscrew pre-load is not adjusted in routine
lubrication work and its value is recorded on commissioning sheet
CM-CNC3X-01, which is not part of this document collection.

## Documentation gaps

Not contained in this schedule:

- The ballscrew pre-load settings for the X, Y and Z axes, which are on
  commissioning sheet CM-CNC3X-01, not in this document collection.
- The lubricant intervals and quantities for the CNC-3XL linear rail variant,
  whose guideways are grease lubricated rather than oil lubricated.
- The side magazine chain replacement interval and the chain tension figure,
  which are in the machine manual.
- The guideway wipe and gib adjustment intervals, which are in the machine
  manual preventive section.

## Appendix: Lubricant cross reference and application points

The machine uses several lubricants and each application point must receive
the correct product. Mixing products or substituting a product without
approval damages the machine and voids the warranty.

| Application point | Product | Quantity | Interval | Method |
| --- | --- | --- | --- | --- |
| Way lubrication, X axis | ISO VG 68 way oil | 0.7 gal | Automatic, weekly check | Pump |
| Way lubrication, Y axis | ISO VG 68 way oil | 0.5 gal | Automatic, weekly check | Pump |
| Way lubrication, Z axis | ISO VG 68 way oil | 0.7 gal | Automatic, weekly check | Pump |
| Ball screw, X axis | Grease X, NLGI 2 | 0.2 oz | Every 2000 hours | Grease gun |
| Ball screw, Y axis | Grease X, NLGI 2 | 0.2 oz | Every 2000 hours | Grease gun |
| Ball screw, Z axis | Grease X, NLGI 2 | 0.2 oz | Every 2000 hours | Grease gun |
| Spindle cartridge | Spindle grease | As service kit | On replacement | Service |
| Tool magazine | Grease X, NLGI 2 | 0.35 oz | Every 1000 hours | Grease gun |
| Chuck grease nipple | Chuck grease | 0.1 oz | Weekly | Grease gun |
| Tailstock | ISO VG 68 way oil | 0.13 gal | Monthly | Oil can |

The reservoir is checked weekly and topped up with the correct product. A
reservoir that empties faster than expected is investigated.

## Appendix: Lubrication fault symptoms and causes

Lubrication faults rarely appear as lubrication faults. They appear as
accuracy drift, surface finish problems or premature component wear.

| Symptom | Likely lubrication cause | Check |
| --- | --- | --- |
| Poor surface finish on one axis | Low way oil or blocked metering unit | Reservoir level and metering output |
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
| Way lubrication | ISO VG 46, BM-W46 | 1.6 gal reservoir | top up weekly, change annually |
| Spindle lubrication | grease, BM-S2 | sealed for life | at 12000 running hours |
| Ball-screw lubrication | grease, BM-B2 | 1 oz per screw | every 2000 running hours |
| Linear guide grease | grease, BM-L2 | 0.4 oz per block | every 2000 running hours |
| Tool changer cam | grease, BM-C1 | 0.7 oz | every 3000 running hours |
| Coolant | water miscible, 6 to 8 percent | 53 gal tank | measure weekly, change every 3000 hours |
| Hydraulic chuck oil | ISO VG 32 | 1.1 gal | every 4000 running hours |
| Automatic greaser cartridge | BM-G4 | 1 | when the low-level alarm shows |

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
| Rev 1 | 2024-02-26 | First controlled issue, aligned with the machine manual issued 2023. |
