Set xl = CreateObject("Excel.Application")
xl.Visible = False

Set oFSO = CreateObject("Scripting.FileSystemObject")
strScriptDirectory = oFSO.GetParentFolderName(WScript.ScriptFullName)
Set wb = xl.Workbooks.Open(strScriptDirectory & "\SM8 Invoices Analysis.xlsm")

xl.Run "Module1.ExportCSV" ' Must match the macro name
wb.Close SaveChanges=True
xl.Quit
Set wb = Nothing
Set xl = Nothing