param(
    [Parameter(Mandatory=$true)][string]$Workbook,
    [string]$Report = (Join-Path $PSScriptRoot 'raport_excel.json')
)
$ErrorActionPreference = 'Stop'
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$suite = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'cazuri_test.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$source = (Resolve-Path -LiteralPath $Workbook).Path
if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -cne $manifest.sha256) {
    throw 'Workbook SHA-256 differs from the locked reference. No calculation performed.'
}
$rows = [System.Collections.Generic.List[object]]::new()
$excel = $null
$book = $null
$fatal = $null
$version = $null
$checked = 0
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AskToUpdateLinks = $false
    $excel.AutomationSecurity = 3
    $version = [string]$excel.Version
    foreach ($case in $suite.cases) {
        # The original is read-only and is never saved; every case starts from it.
        $book = $excel.Workbooks.Open($source, 0, $true)
        $excel.Calculation = -4135
        foreach ($prop in $case.inputs.PSObject.Properties) {
            $parts = $prop.Name.Split('!')
            $cell = $book.Worksheets.Item($parts[0]).Range($parts[1])
            try {
                if ($cell.HasFormula) { throw ('Input overwrites formula: ' + $prop.Name) }
                $value = $prop.Value
                if ($null -eq $value) { $cell.ClearContents() | Out-Null }
                elseif ($value -is [string]) {
                    # Preserve numeric-looking text for the ISNUMBER regression case.
                    if ($value -match '^[-+]?\d+([.,]\d+)?$') { $cell.NumberFormat = '@' }
                    $cell.Value2 = [string]$value
                }
                else { $cell.Value2 = [double]$value }
            } finally {
                [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($cell)
            }
        }
        $excel.CalculateFullRebuild()
        foreach ($prop in $case.expected.PSObject.Properties) {
            $parts = $prop.Name.Split('!')
            $cell = $book.Worksheets.Item($parts[0]).Range($parts[1])
            try { $actual = $cell.Value2 }
            finally { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($cell) }
            $expected = $prop.Value
            $ok = $false
            if ($null -eq $expected -or ($expected -is [string] -and $expected -ceq '')) {
                $ok = ($null -eq $actual -or ($actual -is [string] -and $actual -ceq ''))
            } elseif ($expected -is [string]) {
                $ok = ($actual -is [string] -and $actual -ceq $expected)
            } elseif ($actual -is [double] -or $actual -is [int] -or $actual -is [decimal]) {
                $tol = [double]$suite.numeric_tolerance
                if ($prop.Name -match '^Double_Chance![LM][456]$') { $tol = 0.0 }
                $ok = [Math]::Abs([double]$actual - [double]$expected) -le $tol
            }
            $checked++
            if (-not $ok) {
                $rows.Add([pscustomobject]@{case=$case.id;cell=$prop.Name;expected=$expected;actual=$actual})
            }
        }
        $book.Close($false)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($book)
        $book = $null
    }
} catch {
    $fatal = $_.Exception.Message
} finally {
    if ($null -ne $book) {
        $book.Close($false)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($book)
    }
    if ($null -ne $excel) {
        $excel.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
$passed = ($rows.Count -eq 0 -and $null -eq $fatal -and $checked -gt 0)
$result = [ordered]@{
    passed=$passed;excel_version=$version;source_sha256=$manifest.sha256
    cases=$suite.cases.Count;comparisons=$checked;failures=$rows.ToArray();fatal_error=$fatal
}
$result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Report -Encoding UTF8
if (-not $passed) { Write-Output ('FAIL: ' + $rows.Count + ' mismatches. Report: ' + $Report); exit 1 }
Write-Output ('PASS: ' + $suite.cases.Count + ' cases, ' + $checked + ' comparisons. Report: ' + $Report)
exit 0
