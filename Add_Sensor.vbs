Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = True

Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
excelFilePath = currentDir & "\Cansat_Power_Budget.xlsx"

If Not fso.FileExists(excelFilePath) Then
    MsgBox "Cannot find Cansat_Power_Budget.xlsx!", vbCritical, "Error"
    WScript.Quit
End If

Set objWorkbook = objExcel.Workbooks.Open(excelFilePath)
Set objWorksheet = objWorkbook.Worksheets("Power Budget")

' Find the row that says "--- PACK A (AVIONICS) SUMMARY ---" to insert above it
Dim summaryRow
summaryRow = 1
Do While objWorksheet.Cells(summaryRow, 1).Value <> "--- PACK A (AVIONICS) SUMMARY ---"
    summaryRow = summaryRow + 1
    If summaryRow > 500 Then
        MsgBox "Could not find the Summary block!", vbCritical, "Error"
        WScript.Quit
    End If
Loop

' Prompt user for sensor details
packName = InputBox("Enter Battery Pack (Type 'Pack A' or 'Pack B'):", "Add Sensor/Component", "Pack A")
If packName = "" Then WScript.Quit

subsystem = InputBox("Enter Subsystem (e.g., Avionics, Sensors, Power):", "Add Sensor/Component")
compName = InputBox("Enter Component Name (e.g., New IMU):", "Add Sensor")
voltage = InputBox("Enter Voltage (V):", "Add Sensor", "3.3")
peakI = InputBox("Enter Peak Current (mA):", "Add Sensor", "10")
sleepI = InputBox("Enter Sleep Current (mA):", "Add Sensor", "0.1")
duty = InputBox("Enter Duty Cycle (%):", "Add Sensor", "100")

' Insert row right above the summary block (leave a blank line if it was there)
Dim newRow
newRow = summaryRow - 2
objWorksheet.Rows(newRow).Insert

' Populate data
objWorksheet.Cells(newRow, 1).Value = packName
objWorksheet.Cells(newRow, 2).Value = subsystem
objWorksheet.Cells(newRow, 3).Value = compName
objWorksheet.Cells(newRow, 4).Value = CDbl(voltage)
objWorksheet.Cells(newRow, 5).Value = CDbl(peakI)
objWorksheet.Cells(newRow, 6).Value = CDbl(sleepI)
objWorksheet.Cells(newRow, 7).Value = CDbl(duty)

' Add formulas for the new row
objWorksheet.Cells(newRow, 8).Formula = "=E" & newRow & "*(G" & newRow & "/100)+F" & newRow & "*(1-G" & newRow & "/100)"
objWorksheet.Cells(newRow, 9).Formula = "=D" & newRow & "*E" & newRow
objWorksheet.Cells(newRow, 10).Formula = "=D" & newRow & "*H" & newRow

' Find Pack A Summary range and update SUMIF range automatically
Dim endDataRow
endDataRow = newRow ' The last row of actual data
objWorksheet.Cells(summaryRow + 1, 2).Formula = "=SUMIF(A2:A" & endDataRow & ", ""Pack A"", I2:I" & endDataRow & ")"
objWorksheet.Cells(summaryRow + 2, 2).Formula = "=SUMIF(A2:A" & endDataRow & ", ""Pack A"", J2:J" & endDataRow & ")"

' Update Pack B Summary range automatically
Dim packBRow
packBRow = summaryRow + 8
objWorksheet.Cells(packBRow + 1, 2).Formula = "=SUMIF(A2:A" & endDataRow & ", ""Pack B"", I2:I" & endDataRow & ")"
objWorksheet.Cells(packBRow + 2, 2).Formula = "=SUMIF(A2:A" & endDataRow & ", ""Pack B"", J2:J" & endDataRow & ")"

' Save workbook
objWorkbook.Save
MsgBox "Sensor added successfully and dual-pack formulas updated!", vbInformation, "Success"
