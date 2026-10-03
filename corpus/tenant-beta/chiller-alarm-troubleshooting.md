---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-TS-CH450-1"
source_id: "BM-DOC-2312"
title: "BETA-CH-450 Air Cooled Chiller - Alarm and Fault Troubleshooting Guide"
equipment: "BETA-CH-450"
equipment_also_covers: "none"
document_type: "troubleshooting-guide"
document_type_name: "Troubleshooting guide"
revision: "Rev 1"
effective_date: "2024-09-09"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BM-MAN-CH450-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-CH-450 Air Cooled Chiller - Alarm and Fault Troubleshooting Guide

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-TS-CH450-1 |
| Source identifier | BM-DOC-2312 |
| Equipment | BETA-CH-450 |
| Also covers | none |
| Document type | Troubleshooting guide |
| Revision | Rev 1 |
| Effective date | 2024-09-09 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | BM-MAN-CH450-1 |
| Document owner | Maintenance Engineering |

## Purpose

This guide covers the alarm and fault handling of the BETA-CH-450 air cooled
screw chiller, 450 kW, serving the process cooling in the Line 1 machining
cell.

The alarm code set of this controller is the F, H and E set listed under Alarm
codes used by this controller. It is not the A-series set used on chiller controllers from other
manufacturers. Confirm the code set from the controller display before using
Alarm codes used by this controller, and never quote an alarm code from another
unit's guide.

## Technical data

| Parameter | Value |
| --- | --- |
| Nominal capacity, at rating condition | 450 kW cooling at 45 degF leaving water, 95 degF ambient |
| Refrigerant | R-1234ze |
| Chilled water flow | 82 m3/h |
| Chilled water, supply set point, operating value | 46 degF |
| Chilled water, return, design | 56 degF |
| Maximum ambient for full capacity | 95 degF |
| Design condenser air flow | 5.4 m/s across the coil |
| Glycol | inhibited glycol, 25 percent minimum by volume |
| Controller firmware | 5.x series uses the F, H and E alarm codes |
| Freeze protection | trip when evaporator outlet water is 44 degF or lower |
| High head pressure trip | discharge at or above 217 psi |

The nominal capacity of 450 kW is the manufacturer's rating condition: the duty the
unit is certified to deliver at 45 degF leaving water and 95 degF ambient. The supply
set point of 46 degF is the operating value the plant control runs to day to day.
These two figures answer different questions and are not in conflict. The unit is
rated one degree below its normal operating temperature, so at the 46 degF set point
it delivers at least the rated 450 kW. A question about what the machine is
capable of must be answered with the 45 degF rating condition; a question about
what the plant is running to must be answered with the 46 degF operating set point.

The 95 degF ambient limit is a hard limit. Above it the unit cannot make its
rated capacity and will eventually trip on high head pressure. A day when the
site maximum ambient exceeded 95 degF must be recorded before the fault is
attributed to the machine.

## Alarm codes used by this controller

| Code | Text on display | Meaning |
| --- | --- | --- |
| F-13 | COMPRESSOR HP | Compressor tripped on high discharge pressure, 217 psi or above |
| F-21 | OIL LEVEL LOW | Oil level switch open, or oil differential low |
| F-32 | SUCTION LP | Suction pressure below the low limit |
| F-44 | COMP STARTSW | Compressor failed to start within the start time |
| F-51 | COMM LOSS | Controller lost communication with the plant module |
| H-04 | E-HEAT STAGE | Electric heater stage fault or lockout |
| E-07 | FREEZE STAT | Evaporator outlet water at or below 44 degF |
| E-12 | FLOW SW OPEN | Evaporator flow switch did not prove |
| E-19 | COND FAN | Condenser fan speed or feedback fault |

A code that is not in this table is not documented here. Record the code,
photograph the display, and raise a documentation request.

## Section 4: the unit trips intermittently, repeated F-13

The most common report on this unit is "it trips at random". The code is
F-13, high head pressure, and it has at least seven documented causes:

1. Ambient air above 95 degF. Check the site weather station reading for the
   trip time first. This is the most frequent cause and it is not a machine
   fault.
2. Condenser coil fouled with dust or process debris. Check the fin face.
3. Condenser fan failure or fan speed below set point. Check E-19 in the
   history.
4. Refrigerant overcharge, or a non-condensable gas in the system.
5. Glycol concentration below 25 percent, or the wrong glycol, causing poor
   heat transfer at the evaporator and high suction pressure.
6. Partially blocked evaporator plate heat exchanger from scale.
7. Safety valve lifting and not reseating, or a pressure transmitter out of
   calibration.

Discriminating steps, in order:

1. Read the site ambient temperature at the trip time from the history. If it
   was above 95 degF, the cause is external conditions; the machine is not
   diagnosed before the conditions are corrected.
2. Read the discharge pressure and the saturated condensing temperature from
   the trend history for the 15 minutes before the trip.
3. Check the condenser coil from the ground. Do not climb the unit.
4. Check the glycol concentration with a refractometer for the inhibitor
   package, not for ethylene glycol.
5. Compare the evaporator approach temperature. A large approach with a clean
   condenser indicates a refrigerant side or a glycol side problem, not a
   compressor problem.

Do not reset the unit and leave it. Three F-13 trips in one shift stops the
unit until the cause is established.

## Section 5: repeated E-07 freeze protection trips

Causes, in order:

1. Chilled water flow too low because a pump is on manual, a strainer is
   blocked, or a valve is closed.
2. Set point too low for the load. Check the supply set point against the
   design value in Technical data.
3. Thermistor drift. Compare the evaporator outlet water temperature on the
   control panel with a calibrated contact thermometer at the same point. A
   difference above 3 degF is a sensor fault, not a process fault.
4. Low glycol concentration or air in the water circuit.
5. Thermostat or capillary failure causing the valve to close late.

A freeze trip resets automatically once the water is above 48 degF. If it
repeats, the automatic reset is not an acceptance criterion; establish the
cause first.

## Section 6: E-12 flow switch open

Causes: pump on manual, strainer blocked, flow switch not proved, valve
closed, or a pump in the parallel pair that has failed.

Check the pump status and the strainer differential first. A flow switch
failure is confirmed only after the flow path has been proven clear.

## Section 7: F-21 oil level low

Causes: oil level switch fault, genuine oil loss from a leak, oil carryover
to the evaporator, or an oil drain valve left open.

Confirm the oil level in the compressor sight glass first. If oil is present
and the switch is open, the switch is faulty; if oil is low, find the leak. An
oil drain valve left open has caused two F-21 calls on this unit.

## Section 8: H-04 electric heater stage fault

The unit uses an electric heater stage in the evaporator for low load control
and freeze protection. Causes: open heater element, failed contactor, failed
high limit thermostat, or a control fault.

Check the high limit thermostat first: a stuck closed thermostat presents as a
heater stage fault with a healthy element. The heater element resistance values
are in the vendor manual and are not in this document collection.

## Escalation

Escalate to Maintenance Engineering and the controls engineer when: three
trips of the same code occur in one shift; a trip cannot be explained by the
ambient conditions or the set points; the controller firmware does not match
Technical data; or the required figure is not in the controlled document set. The
work order carries documentation status "insufficient information" in those
cases.

## Documentation gaps

Not contained in this guide:

- The alarm code map for controllers with firmware 4.x and earlier, which used
  a different code set. The map is Appendix 3 of the vendor manual, which is
  not in this document collection.
- The refrigerant charge quantity for this unit, which is on the equipment
  nameplate.
- The glycol inhibitor package specification and the interval for adding
  inhibitor.
- The pressure transmitter calibration procedure.
- The heater element resistance values.

## Appendix: Extended alarm and fault matrix

This matrix extends the alarm codes and symptoms in the main sections with the
verification steps and the most likely cause for each.

| Code | Verification step | Most likely cause | First action |
| --- | --- | --- | --- |
| F-13 | Read ambient and discharge pressure | Ambient above 95 degF | Record conditions, do not reset |
| F-13 | Check the condenser coil | Coil fouled | Clean the coil |
| F-21 | Read the oil level at the sight glass | Low oil level | Top up and find the leak |
| F-32 | Check the suction pressure | Low charge | Leak test and recharge |
| F-44 | Check the compressor start sequence | Start fault | Investigate the contactor |
| F-51 | Check the communication cable | Module fault | Reset or replace the module |
| H-04 | Check the heater stage and high limit | Stuck high limit | Replace the thermostat |
| E-07 | Compare the thermistor to a contact thermometer | Thermistor drift | Replace the thermistor |
| E-12 | Check the flow switch and strainer | Strainer blocked | Clean the strainer |
| E-19 | Check the fan feedback | Fan or feedback fault | Repair the fan circuit |

A code that is not in the table is recorded with a photograph and reported as
an undocumented code. The controller firmware version is recorded with the
code because the code set changes between versions.

## Appendix: Seasonal and condition-based checks

Chiller faults cluster around weather and load. This appendix lists the checks
brought forward when the season changes or when the load changes.

Before the warm season:

- Clean the condenser coil and confirm the airflow is unobstructed.
- Test the condenser fans and confirm the speed feedback.
- Confirm the refrigerant charge by the subcooling and superheat method.
- Confirm the glycol concentration for the expected minimum temperature.
- Test the high-pressure trip and confirm the set point.
- Confirm the ambient sensor reads correctly against a reference.

Before the cold season:

- Confirm the freeze protection set point and test the trip.
- Confirm the glycol concentration for the lower ambient.
- Confirm the heater stage, if fitted, operates and the high limit is set.
- Confirm the water circuit is protected against freezing when idle.

After a load change:

- Re-check the flow against the design value.
- Re-check the approach temperatures against the baseline.
- Re-check the compressor current against the nameplate.
- Re-check the controller set points against the design values.

Each check is recorded with the date and the measured value. A check that is
not recorded is treated as not done.

## Appendix: Refrigerant, instrumentation and electrical reference

| Item | Value |
| --- | --- |
| Refrigerant | R-134a, charge 31 lb |
| Refrigerant top-up | by weight only, never by pressure |
| Low pressure switch | 29 psi cut-out, 51 psi cut-in |
| High pressure switch | 348 psi cut-out, manual reset |
| High head pressure alarm | F-13 |
| Running current, compressor | 42 A per phase |
| Supply | 460 V, 3 phase, 60 Hz |
| Ambient limit | 95 degF |
| Leaving water set point | 46 degF |
| Freeze protection | 48 degF reset |
| Glycol minimum | 25 percent by volume |

Refrigerant is added by weight from a calibrated cylinder and the quantity is
recorded in the refrigeration log. Adding refrigerant until the suction
pressure looks right is prohibited because it hides a leak and overcharges the
circuit. A circuit that needs a top-up twice in a season is leak tested before
it is returned to service.

Instrumentation used for fault finding must be within its calibration date.
Pressure gauges are read at the service port with the schrader core depressed
for no longer than necessary. Clamp meters are placed on a single conductor;
placing the clamp around a cable carrying both supply and return reads zero and
is not a valid measurement.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2024-09-09 | First controlled issue, compiled from Line 1 fault history 2022 to 2024. |
