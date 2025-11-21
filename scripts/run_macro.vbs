Set xl = CreateObject("Excel.Application")
xl.Visible = False

Set oFSO = CreateObject("Scripting.FileSystemObject")
strScriptDirectory = oFSO.GetParentFolderName(WScript.ScriptFullName)
filePath = oFSO.BuildPath(strScriptDirectory & "\..", "Export.xlsm")
Set wb = xl.Workbooks.Open(filePath)

WScript.Echo "Running Excel Macro. This may take up to 3 minutes. Please click OK and wait for the next popup window to show up."
xl.Run "Module1.ExportCSV" ' Must match the macro name
wb.Close SaveChanges=True
xl.Quit
Set wb = Nothing
Set xl = Nothing
WScript.Echo "VBA Script has been completed, the output window has been opened."