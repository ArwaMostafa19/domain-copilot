---
tenant: "tenant-beta"
tenant_name: "Beta Manufacturing"
site: "Harbor Works, Line 1 (imperial documentation)"
doc_id: "BETA-DIA-P100-1"
source_id: "BM-DOC-2262"
title: "BETA-P-100 Duplex Hydraulic Power Unit - Diagnostic Procedure"
equipment: "BETA-P-100"
equipment_also_covers: "none; BETA-P-110 is out of scope, see Limitations and documentation gaps"
document_type: "diagnostic-procedure"
document_type_name: "Diagnostic procedure"
revision: "Rev 1"
effective_date: "2024-07-08"
status: "current"
supersedes: ""
applies_to: "Assets listed under equipment for Beta Manufacturing"
related_documents: "BETA-MAN-HP200-B, BETA-TS-HP200-1, BETA-SAF-HP200-ECP-1"
document_owner: "Maintenance Engineering"
source_format: "markdown"
generator: "scripts/generate_corpus.py"
---

# BETA-P-100 Duplex Hydraulic Power Unit - Diagnostic Procedure

| Field | Value |
| --- | --- |
| Tenant | Beta Manufacturing (tenant-beta) |
| Site | Harbor Works, Line 1 (imperial documentation) |
| Document identifier | BETA-DIA-P100-1 |
| Source identifier | BM-DOC-2262 |
| Equipment | BETA-P-100 |
| Also covers | none; BETA-P-110 is out of scope, see Limitations and documentation gaps |
| Document type | Diagnostic procedure |
| Revision | Rev 1 |
| Effective date | 2024-07-08 |
| Status | current |
| Applies to | Assets listed under equipment |
| Related documents | BETA-MAN-HP200-B, BETA-TS-HP200-1, BETA-SAF-HP200-ECP-1 |
| Document owner | Maintenance Engineering |

## Purpose and scope

This procedure covers diagnosis of the duplex hydraulic power unit
BETA-P-100, which supplies the BETA-HP-200 press, and the measurement methods
that the press troubleshooting guide calls.

It does not cover:

- BETA-P-110, the bench power unit on the BETA-HP-100 in the maintenance
  shop. Its accumulator size, its decay test value and its changeover
  arrangement are different and are not recorded in this document collection.
- The press mechanical and control faults, which are in the press manual and
  the troubleshooting guide.

Pressure set points are not repeated here. The authorised set points are those
of the current controlled revision of the press manual. Do not set the power
unit from a value written in a work order, copied from another unit on the
site, or converted into metric.

## Test points and instruments

| Point | Location | Use |
| --- | --- | --- |
| TP-1 | Pump outlet, before the suction strainer | Suction pressure, cavitation check |
| TP-2 | After the pumps, before the main relief | Flow measurement and pressure decay |
| TP-3 | Manifold, downstream of the main relief | Working pressure |
| TP-4 | Return line, before the filter | Return pressure and differential |
| SP-2 | Small valve on the return line | Oil sampling |

Required instruments, each with a valid calibration certificate: 3000 psi test
gauge with 50 psi graduations, 5000 psi test gauge with 100 psi graduations,
clamp-on flow meter covering 0 to 40 gpm, tachometer, clamp meter on the motor
supply, and a timing device for the decay test.

## Safety prerequisites

1. Permit LOTO-4410 is open for the specific test.
2. BETA-SAF-HP200-ECP-1 steps 1 to 8 are complete: electrical isolation at panel
   3B-11, HX-301, HX-302 and HX-311 closed and locked, die cushion released
   and blocked with CB-9, accumulator AC-2 bled through BV-321 into drain drum
   DD-2, ram block RB-6 and tie-off fitted.
3. The accumulator gauge reads 10 psi or less, verified on the day by the
   person doing the work.
4. The cushion pressure gauge reads 0 psi.
5. Attempt start has been performed from the operator station and produced no
   motion, witnessed by a second authorised person.
6. The red verification tag is attached and signed by both people.
7. Every port opened is capped or blanked the same hour. Discharged oil goes
   into DD-2, never onto the floor and never into a drain.
8. Gauges are bled to zero before any cap is removed.

Test 1, the suction pressure check, may be done with the circuit live because
it is a measurement only, and only below the maximum working pressure in the
current press manual revision.

Test 6 is an exception to the isolation requirement. Recording motor current
and supply voltage needs the motors energized, which the prerequisites above
forbid. Test 6 is therefore performed under a separate energization permit
issued by EHS, with the light curtain active, the guards closed and the
hydraulic circuit depressurised and blocked. The isolation in the prerequisite
list is not removed for any other reason, and no hydraulic work may be in
progress while Test 6 is energized.

A diagnostic measurement is never a reason to work with the circuit charged.

## Test 1: suction pressure and cavitation check

1. Run pump A alone for 5 minutes at idle with the die area empty and record
   the pressure at TP-1 and TP-3.
2. Repeat with pump B alone. The two tests must be compared, not averaged.
3. Record motor current for each pump and pump speed in rpm.
4. Record oil temperature.

Interpretation:

- Low suction pressure with audible cavitation and falling flow indicates a
  blocked strainer, a collapsed suction hose or a low reservoir level.
- Correct suction pressure with reduced flow indicates pump wear.
- A difference of more than 10 percent between pump A and pump B flow means one
  pump is degraded. A degraded pump is not left in service as a silent loss of
  reserve.
- Correct pressure and flow with high current indicates a mechanical drag,
  usually the coupling.

## Test 2: main relief valve lift-off and seating

1. Disconnect the press feed downstream of TP-2 and cap it. Work with the
   press feed isolated, not with the press connected.
2. Fit the 5000 psi test gauge at TP-2.
3. Increase pump demand in 25 psi steps and record the pressure at which flow
   starts at a dead pump.
4. Reduce demand and record the pressure at which flow stops.

Interpretation:

- Lift-off more than 50 psi below the set point in the current press manual
  revision means the relief valve is worn. The valve is not adjusted; it is
  replaced.
- Seating pressure more than 100 psi below lift-off means external leakage
  past the valve. Investigate the return line and the pilot circuit first.
- A stable lift-off 50 to 150 psi above the authorised set point is an
  escalation, not a pass. Repeated operation above the pressure trip is not
  permitted.

## Test 3: flow measurement

Fit the clamp-on flow meter at TP-2 with the circuit dead, run each pump
separately for 2 minutes and record the flow.

- Flow more than 10 percent below the figure on the pump data plate means pump
  wear. The pump is not repaired on site; the exchange unit is fitted.
- Flow correct with pressure too low means the relief valve is lifting early.
  Go to test 2.
- Flow correct and pressure correct with the ram not rising means a control
  fault, not a power unit fault. Go to the troubleshooting guide.

## Test 4: pressure decay test

1. With the pumps isolated and locked, pressurise the main circuit from a
   separate test pump to 1000 psi.
2. Disconnect the test pump and cap its outlet.
3. Record the pressure at TP-3 at time zero and at 1 minute intervals for 10
   minutes. Isolate the accumulator from the manifold during this test so the
   accumulator does not mask the decay.
4. Plot the decay. Normal internal leakage gives a decay of no more than
   50 psi over 10 minutes.

Interpretation:

- Decay above 50 psi in 10 minutes at 1000 psi indicates internal leakage.
  Confirm the source by isolating the cylinder feed from the manifold and
  repeating. A decay that persists with the cylinder isolated is a leak
  upstream of the manifold: the ram seal, the rod seal or the cylinder.
- Decay below 10 psi over 10 minutes together with a symptom of unstable
  pressure means the leak is not in the cylinder. Investigate the transducer,
  the counterbalance circuit and the die height sensor line.
- No decay and no pressure means the gauge or transducer is faulty. Cross-check
  at TP-2.

The test pressure of 1000 psi and the 50 psi decay limit apply to this power
unit at 100 degF oil temperature. A decay figure from another unit, another oil
or another unit system is not an acceptance value.

## Test 5: duplex pump changeover test

The duplex arrangement means that a pump can fail silently while the press
still works, on one pump only. This test exists because that failure was the
cause of an unstable pressure report that was misdiagnosed three times.

1. Select pump A alone and run 3 working strokes with an empty die. Record the
   pressure trace.
2. Select pump B alone and repeat.
3. Select both pumps and repeat.
4. Force a changeover during a stroke by selecting both, then pump A, then
   both, using the selector at the operator station. Record the pressure
   transient at each change.

Acceptance:

- No pressure step greater than 50 psi at any changeover.
- The traces for pump A and pump B agree within 10 percent.
- No cavitation noise on either pump.

Acceptance interval: every 2000 running hours and after any changeover fault.
A failed changeover test is a stop condition for the duplex arrangement: the
press runs on one pump until it is repaired.

## Test 6: motor and drive

Record motor current in amps, supply voltage and the voltage balance across
the three phases for each pump.

Voltage imbalance above 2 percent causes motor heating that is regularly
misdiagnosed as a pump fault. A current reading above the nameplate value at
rated flow is an escalation: check the pump for wear at the same time as the
motor.

## Limitations and documentation gaps

Not in this procedure:

- The decay limit and accumulator values for the BETA-P-110 bench unit on the
  BETA-HP-100.
- Pump internal clearances and vendor wear limits, which are on the pump data
  sheets.
- The changeover valve service interval and the shim figures, which are on the
  changeover valve data sheet.
- The power unit controller alarm code list, which is read from the controller
  and not transcribed here.
- The oil analysis laboratory acceptance report format.

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
| Pressure gauge, low | 0 to 360 psi | 0.5 percent full scale | 12 months |
| Pressure gauge, high | 0 to 5800 psi | 1 percent full scale | 12 months |
| Flow meter | 0 to 26 gpm | 2 percent of reading | 12 months |
| Tachometer | 0 to 3000 rpm | 1 rpm | 12 months |
| Clamp meter, current | 0 to 200 A | 2 percent of reading | 12 months |
| Multimeter, voltage | 0 to 600 V | 1 percent of reading | 12 months |
| Thermometer | 32 to 300 degF | 2 degF | 12 months |
| Particle counter | ISO 4406 range | As specified | 12 months |

An instrument without a valid certificate is not used. A test performed with
an out-of-calibration instrument is repeated with a calibrated instrument
before the result is recorded.

## Appendix: Test sheet template and expected values

The test sheet below is completed for every diagnostic visit. The expected
value column is completed from the equipment manual before the test starts.

| Test | Measurement point | Expected value | Tolerance | Recorded |
| --- | --- | --- | --- | --- |
| Suction pressure | TP-1 | 15 to 45 psi | Plus or minus 15 psi | |
| Main relief lift-off | TP-3 | 2000 psi | Plus or minus 70 psi | |
| System flow | TP-2 | 16 gpm | Plus or minus 1 gpm | |
| Pressure decay at hold | TP-3 | Less than 70 psi per minute | As specified | |
| Return pressure | TP-4 | 30 psi | Plus or minus 7 psi | |
| Oil temperature | Reservoir | 104 to 122 degF | Maximum 140 degF | |
| Motor current | Clamp at motor | Within nameplate | Plus or minus 5 percent | |
| Motor voltage balance | Motor terminals | Balanced | Maximum 2 percent | |

A reading outside tolerance is entered in red and triggers a follow-up test.
The follow-up test and its result are recorded on the same sheet. A test sheet
without the expected values completed first is not a valid record.

## Revision history

| Revision | Effective date | Summary |
| --- | --- | --- |
| Rev 1 | 2024-07-08 | First controlled issue, after the 2024 duplex changeover fault review. |
