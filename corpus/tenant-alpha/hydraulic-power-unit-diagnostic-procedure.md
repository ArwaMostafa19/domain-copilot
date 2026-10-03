---
tenant: "tenant-alpha"
tenant_name: "Alpha Manufacturing"
site: "Ridgeway Works, Building 2 (metric documentation)"
doc_id: "ALPHA-DIA-P100-1"
source_id: "AM-DOC-1103"
title: "ALPHA-P-100 Hydraulic Power Unit - Diagnostic Procedure"
equipment: "ALPHA-P-100"
equipment_also_covers: "none; ALPHA-P-100A is out of scope, see Limitations and documentation gaps"
document_type: "diagnostic-procedure"
document_type_name: "Diagnostic procedure"
revision: "Rev 1"
effective_date: "2024-06-10"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Alpha Manufacturing"
related_documents: "ALPHA-MAN-HP200-B, ALPHA-TS-HP200-1, ALPHA-SAF-HP200-LOTO-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# ALPHA-P-100 Hydraulic Power Unit - Diagnostic Procedure

| Field | Value |
| --- | --- |
| Tenant | Alpha Manufacturing (tenant-alpha) |
| Site | Ridgeway Works, Building 2 (metric documentation) |
| Document identifier | ALPHA-DIA-P100-1 |
| Source identifier | AM-DOC-1103 |
| Equipment | ALPHA-P-100 |
| Also covers | none; ALPHA-P-100A is out of scope, see Limitations and documentation gaps |
| Document type | Diagnostic procedure |
| Revision | Rev 1 |
| Effective date | 2024-06-10 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | ALPHA-MAN-HP200-B, ALPHA-TS-HP200-1, ALPHA-SAF-HP200-LOTO-1 |
| Document owner | Maintenance Engineering |

## Purpose and scope

This procedure covers diagnosis of the hydraulic power unit ALPHA-P-100,
which supplies the ALPHA-HP-200 press, and the measurement methods that the
press troubleshooting guide calls.

It does not cover:

- P-100A, the alternative skid with a plate oil cooler and a 10 litre nitrogen
  accumulator, fitted to the bench press ALPHA-HP-210. Its accumulator
  pre-charge, its cooler arrangement and its leak-down acceptance value are
  different and are not recorded in this document collection.
- Power unit ALPHA-P-110 on the HP-210 bench press.
- The press mechanical and control faults; those are in the press manual and
  the troubleshooting guide.

Pressure set points are deliberately not repeated here. The authorised set
points are those of the current controlled revision of the press manual, and
the power unit is not to be set from a value written in a work order or copied
from another unit.

## Test points and instruments

| Point | Location | Use |
| --- | --- | --- |
| TP-1 | Pump outlet, before the suction strainer | Suction pressure, cavitation check |
| TP-2 | After the pump, before the main relief | Flow measurement and pressure decay |
| TP-3 | Manifold, downstream of the main relief | Working pressure |
| TP-4 | Return line, before the filter | Return pressure and differential |
| SP-1 | Small valve on the return line | Oil sampling |

Required instruments, each with a valid calibration certificate: 250 bar test
gauge with 6 bar graduations, 400 bar test gauge with 10 bar graduations,
clamp-on flow meter covering 0 to 100 l/min, laser or dial tachometer, clamp
meter on the motor supply, and a timing device for the decay test.

## Safety prerequisites

Tests 2 to 6 contain work inside the frame, at the manifold or with the
circuit charged. None of them may be started before all of the following are
true and recorded:

1. Permit PTW-2600 is open for the specific test.
2. ALPHA-SAF-HP200-LOTO-1 steps 1 to 6 are complete: electrical isolation at
   panel 3A-04, HV-101 and HV-201 closed and locked, accumulator AC-1 bled
   through BV-103, drain vessel DV-1 fitted, mechanical block and tie-off
   fitted.
3. The accumulator gauge at the power unit reads 5 bar or less, verified on the
   day, by the person doing the work.
4. Attempt start has been performed from the pendant and produced no motion,
   witnessed by a second authorised person.
5. The green zero-energy verification tag is attached and countersigned.
6. Every port opened is capped or blanked the same hour. Discharged oil goes
   into DV-1, never onto the floor and never into a drain.
7. Pressure gauges are bled to zero before any cap is removed.

Test 1, the suction pressure check at TP-1, may be done with the circuit live
because it is a measurement only. It must be done with the circuit below the
maximum working pressure in the current press manual revision.

Test 6 is an exception to the isolation requirement. Recording motor current
and supply voltage needs the motor energized, which the prerequisites above
forbid. Test 6 is therefore performed under a separate energization permit
issued by EHS, with the light curtain active, the guard closed and the
hydraulic circuit depressurised and blocked. The isolation in the prerequisite
list is not removed for any other reason, and no hydraulic work may be in
progress while Test 6 is energized.

A diagnostic measurement is never a reason to work with the circuit charged.

## Test 1: suction pressure and cavitation check

1. Run the pump for 5 minutes at idle, die area empty, and record the pressure
   at TP-1 and at TP-3.
2. Record motor current in amps and pump speed in rpm.
3. Record oil temperature.
4. Repeat with the pump in loaded condition at the pressure stated in the
   press manual.

Interpretation:

- Low suction pressure with audible cavitation and falling flow indicates a
  blocked strainer, a collapsed suction hose or a low reservoir level.
- Correct suction pressure with reduced flow indicates pump wear.
- Correct pressure and flow with high current indicates a mechanical drag, not
  a hydraulic fault. Investigate the drive and the coupling.

No single reading is sufficient. Record all four values together.

## Test 2: main relief valve lift-off and seating

1. Disconnect the press feed downstream of TP-2 and cap it. Work with the
   press feed isolated, not with the press connected.
2. Fit the 400 bar test gauge at TP-2.
3. Increase pump demand in 5 bar steps. Record the pressure at which flow
   starts at a dead pump.
4. Reduce demand. Record the pressure at which flow stops.

Interpretation:

- Lift-off more than 5 bar below the set point in the current press manual
  revision means the relief valve is worn or the seat is damaged. The valve
   is not adjusted; it is replaced.
- Seating pressure more than 10 bar below lift-off means external leakage past
  the valve. Investigate the return line and the pilot circuit before
   condemning the valve.
- A lift-off that is stable but 5 to 15 bar above the authorised set point is
  an escalation, not a pass. The pressure trip in the press manual is the
  protective limit and repeated operation above it is not permitted.

## Test 3: flow measurement

Fit the clamp-on flow meter at TP-2 with the circuit dead, run the pump for
2 minutes, and record the flow.

- Flow more than 10 percent below the figure on the pump data plate means pump
  wear. The pump is not repaired; the exchange unit is fitted.
- Flow correct with pressure too low means the relief valve is lifting early.
  Go to test 2.
- Flow correct and pressure correct with the ram not rising means a control
  fault, not a power unit fault. Go to the troubleshooting guide.

## Test 4: pressure decay test

This test quantifies internal leakage. It is the test that separates the two
causes that look identical on a pressure gauge.

1. With the pump isolated and locked, pressurise the main circuit from a
   separate test pump to the pressure stated in the press manual for the decay
   test. That pressure is 180 bar.
2. Disconnect the test pump. Cap its outlet.
3. Record the pressure at TP-3 at time zero, then at 1 minute intervals for
   10 minutes. Do not read the accumulator gauge during this test; the
   accumulator is isolated by closing the manifold isolation valve.
4. Plot the decay. Normal internal leakage gives a decay of no more than
   6 bar over 10 minutes.

Interpretation:

- Decay above 6 bar in 10 minutes at 180 bar: internal leakage. Confirm the
  source by isolating the cylinder feed from the manifold and repeating; a
  decay that persists with the cylinder isolated is a leak upstream of the
  manifold, that is the ram seal, the rod seal or the cylinder itself.
- Decay below 2 bar over 10 minutes with a symptom of unstable pressure: the
  leak is not internal to the cylinder. Investigate the pressure
  transducer, the counterbalance circuit and the die height sensor line.
- No decay and no pressure: the gauge or the transducer is faulty. Cross-check
  against TP-2.

The decay test figure of 180 bar and the 6 bar limit apply to this power unit
at 20 degC oil temperature. A decay figure from another unit, another oil or a
converted unit system is not an acceptance value.

## Test 5: contamination assessment

Draw two samples, one from SP-1 and one from the bottom of the reservoir,
using a clean sample bottle and a new cap each time.

- ISO 4406 code worse than the limit in the press manual is a failure of the
  oil condition task, not of the power unit.
- A high water content with a stable ISO code indicates a water ingress path,
  usually the reservoir breather. Clean or replace the breather and re-test.
- Metal particles in the pump inlet sample indicate rod or ram wear; escalate
  immediately, because continued running destroys the pump.

## Test 6: motor and drive

Record motor current in amps, supply voltage, and the voltage balance across
the three phases. Voltage imbalance above 2 percent causes a motor heating
problem that is often misdiagnosed as a compressor or pump fault.

A current reading above the nameplate value at rated flow and pressure is an
escalation: check the pump for wear at the same time as the motor.

## Limitations and documentation gaps

The following are not in this procedure:

- P-100A accumulator pre-charge, leak-down acceptance and cooler acceptance
  values. P-100A is fitted to ALPHA-HP-210 and is out of scope here.
- The numerical decay limit for the ALPHA-P-110 power unit on the bench press.
- Pump internal clearances and vendor wear limits. These are on the pump data
  sheets.
- The alarm code list of the power unit controller. Read it from the
  controller; it is not transcribed in this document.

## Escalation

Escalate to Maintenance Engineering when a test result cannot be compared with
a documented acceptance value, when a required value is absent from the
controlled document set, or when two tests give contradictory results. In all
these cases the work order carries documentation status "insufficient
information".

## Appendix: Instrument schedule and calibration requirements

Every instrument used for a diagnostic test must have a calibration
certificate that is valid on the day of the test. The certificate number and
the calibration due date are recorded on the test sheet with the readings.

| Instrument | Range | Accuracy required | Calibration interval |
| --- | --- | --- | --- |
| Pressure gauge, low | 0 to 25 bar | 0.5 percent full scale | 12 months |
| Pressure gauge, high | 0 to 400 bar | 1 percent full scale | 12 months |
| Flow meter | 0 to 100 l/min | 2 percent of reading | 12 months |
| Tachometer | 0 to 3000 rpm | 1 rpm | 12 months |
| Clamp meter, current | 0 to 200 A | 2 percent of reading | 12 months |
| Multimeter, voltage | 0 to 600 V | 1 percent of reading | 12 months |
| Thermometer | 0 to 150 degC | 1 degC | 12 months |
| Particle counter | ISO 4406 range | As specified | 12 months |

An instrument without a valid certificate is not used. A test performed with
an out-of-calibration instrument is repeated with a calibrated instrument
before the result is recorded. The repeat is documented with the reason.

## Appendix: Test sheet template and expected values

The test sheet below is completed for every diagnostic visit. The expected
value column is completed from the equipment manual before the test starts so
that a reading can be judged immediately.

| Test | Measurement point | Expected value | Tolerance | Recorded |
| --- | --- | --- | --- | --- |
| Suction pressure | TP-1 | 1 to 3 bar | Plus or minus 1 bar | |
| Main relief lift-off | TP-3 | 240 bar | Plus or minus 5 bar | |
| System flow | TP-2 | 63 l/min | Plus or minus 3 l/min | |
| Pressure decay at hold | TP-3 | Less than 5 bar per minute | As specified | |
| Return pressure | TP-4 | 2 bar | Plus or minus 0.5 bar | |
| Oil temperature | Reservoir | 40 to 50 degC | Maximum 60 degC | |
| Motor current | Clamp at motor | Within nameplate | Plus or minus 5 percent | |
| Motor voltage balance | Motor terminals | Balanced | Maximum 2 percent | |

A reading outside tolerance is entered in red and triggers a follow-up test.
The follow-up test and its result are recorded on the same sheet. A test sheet
without the expected values completed first is not a valid record.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2024-06-10 | First controlled issue, extracted from the fault investigation reports of 2023 and 2024. |
