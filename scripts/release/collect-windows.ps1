# Read-only on an explicitly approved isolated Windows 11 x64 session; never installs/launches.
param(
  [Parameter(Mandatory=$true)][switch]$ApprovedIsolatedSession,
  [Parameter(Mandatory=$true)][string]$Installer,
  [Parameter(Mandatory=$true)][string]$AppExe,
  [Parameter(Mandatory=$true)][string]$EngineExe,
  [Parameter(Mandatory=$true)][string]$NewOutputDirectory
)
$ErrorActionPreference = 'Stop'
try {
  $osInfo = Get-CimInstance Win32_OperatingSystem
  if (-not $ApprovedIsolatedSession -or $osInfo.Caption -notmatch 'Windows 11' -or
      [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') {
    throw 'TARGET_REQUIRED'
  }
  if (Test-Path -LiteralPath $NewOutputDirectory) { throw 'OUTPUT_MUST_BE_NEW' }
  foreach ($item in @($Installer, $AppExe, $EngineExe)) {
    if (-not (Test-Path -LiteralPath $item -PathType Leaf)) { throw 'INPUT_REQUIRED' }
  }
  New-Item -ItemType Directory -Path $NewOutputDirectory | Out-Null
} catch {
  [Console]::Error.WriteLine('TARGET_INPUT_OR_NEW_OUTPUT_REQUIRED')
  exit 2
}
$step = 'initializing'
function Write-CollectorStatus([string]$Status, [int]$ExitCode) {
  $content = @{ schemaVersion=1; status=$Status; step=$step; exitCode=$ExitCode } | ConvertTo-Json -Compress
  $statusPath = Join-Path $NewOutputDirectory 'collector-status.json'
  $temporaryPath = Join-Path $NewOutputDirectory 'collector-status.json.tmp'
  [System.IO.File]::WriteAllText($temporaryPath, $content, [System.Text.UTF8Encoding]::new($false))
  if ([System.IO.File]::Exists($statusPath)) {
    [System.IO.File]::Replace($temporaryPath, $statusPath, $null)
  } else {
    [System.IO.File]::Move($temporaryPath, $statusPath)
  }
}
function Start-CollectorStep([string]$Name) {
  $script:step = $Name
  Write-CollectorStatus 'pending' 0
}
try {
  Write-CollectorStatus 'pending' 0
  Start-CollectorStep 'pe-reader'
  . (Join-Path $PSScriptRoot 'pe-machine.ps1')
  Start-CollectorStep 'device'
  $cpuInfo = Get-CimInstance Win32_Processor | Select-Object Name, AddressWidth
  $memory = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
  @{ caption=$osInfo.Caption; version=$osInfo.Version; build=$osInfo.BuildNumber;
     architecture=$osInfo.OSArchitecture; cpu=$cpuInfo; memoryBytes=$memory } |
    ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $NewOutputDirectory 'device.json')
  $records = @()
  $index = 0
  foreach ($item in @($Installer, $AppExe, $EngineExe)) {
    Start-CollectorStep "signature-$index"
    $signatureInfo = Get-AuthenticodeSignature -LiteralPath $item
    # Preserve each first raw signature result even when validation or later artifacts fail.
    @{ status=$signatureInfo.Status.ToString(); signer=$signatureInfo.SignerCertificate.Subject;
       timestampSigner=$signatureInfo.TimeStamperCertificate.Subject } |
      ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $NewOutputDirectory "signature-$index.json")
    if ($signatureInfo.Status -ne 'Valid' -or $null -eq $signatureInfo.TimeStamperCertificate) {
      throw 'SIGNATURE_INVALID'
    }
    Start-CollectorStep "pe-$index"
    $machine = Get-PeMachine $item
    if ($index -eq 0 -and $machine -notin @('0x014c', '0x8664')) { throw 'INSTALLER_MACHINE_REQUIRED' }
    if ($index -ne 0 -and $machine -ne '0x8664') { throw 'EXECUTABLE_X64_REQUIRED' }
    Start-CollectorStep "artifact-$index"
    $record = @{ fileName=[System.IO.Path]::GetFileName($item);
       sha256=(Get-FileHash -LiteralPath $item -Algorithm SHA256).Hash;
       machine=$machine; status=$signatureInfo.Status.ToString();
       signer=$signatureInfo.SignerCertificate.Subject;
       timestampSigner=$signatureInfo.TimeStamperCertificate.Subject;
       productVersion=(Get-Item -LiteralPath $item).VersionInfo.ProductVersion }
    $record | ConvertTo-Json -Depth 4 |
      Set-Content -LiteralPath (Join-Path $NewOutputDirectory "artifact-$index.json")
    $records += $record
    $index += 1
  }
  Start-CollectorStep 'artifacts'
  $records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $NewOutputDirectory 'artifacts.json')
  Start-CollectorStep 'scope'
  'Metadata only. Completion is not signature-chain, native-operation or same-package provenance proof. SDK signtool /pa /all, installation, DPAPI and independent review remain separate.' |
    Set-Content -LiteralPath (Join-Path $NewOutputDirectory 'scope.txt')
  $step = 'complete'
  Write-CollectorStatus 'complete' 0
} catch {
  try { Write-CollectorStatus 'failed' 1 } catch {
    # Storage failures leave the prior pending/malformed marker and raw files; verification rejects them.
    [Console]::Error.WriteLine('COLLECTOR_STATUS_WRITE_FAILED')
  }
  [Console]::Error.WriteLine('COLLECTION_FAILED')
  exit 1
}
