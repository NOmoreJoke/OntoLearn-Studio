# Read-only on an explicitly approved isolated Windows 11 x64 session; never installs/launches.
param(
  [Parameter(Mandatory=$true)][switch]$ApprovedIsolatedSession,
  [Parameter(Mandatory=$true)][string]$Installer,
  [Parameter(Mandatory=$true)][string]$AppExe,
  [Parameter(Mandatory=$true)][string]$EngineExe,
  [Parameter(Mandatory=$true)][string]$NewOutputDirectory
)
$ErrorActionPreference = 'Stop'
$osInfo = Get-CimInstance Win32_OperatingSystem
if (-not $ApprovedIsolatedSession -or $osInfo.Caption -notmatch 'Windows 11' -or
    [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') {
  throw 'TARGET_REQUIRED: approved Windows 11 x64 isolated session'
}
if (Test-Path -LiteralPath $NewOutputDirectory) { throw 'OUTPUT_MUST_BE_NEW' }
foreach ($item in @($Installer, $AppExe, $EngineExe)) {
  if (-not (Test-Path -LiteralPath $item -PathType Leaf)) { throw 'INPUT_REQUIRED' }
}
New-Item -ItemType Directory -Path $NewOutputDirectory | Out-Null
$cpuInfo = Get-CimInstance Win32_Processor | Select-Object Name, AddressWidth
$memory = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
@{ caption=$osInfo.Caption; version=$osInfo.Version; build=$osInfo.BuildNumber;
   architecture=$osInfo.OSArchitecture; cpu=$cpuInfo; memoryBytes=$memory } |
  ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $NewOutputDirectory 'device.json')
function Get-PeMachine([string]$FilePath) {
  $stream = [System.IO.File]::OpenRead($FilePath)
  $reader = [System.IO.BinaryReader]::new($stream)
  try {
    if ($reader.ReadUInt16() -ne 0x5a4d) { throw 'PE_MZ_REQUIRED' }
    $stream.Position = 0x3c
    $offset = $reader.ReadUInt32()
    $stream.Position = $offset
    if ($reader.ReadUInt32() -ne 0x00004550) { throw 'PE_SIGNATURE_REQUIRED' }
    return ('0x{0:x4}' -f $reader.ReadUInt16())
  } finally { $reader.Dispose(); $stream.Dispose() }
}
$records = foreach ($item in @($Installer, $AppExe, $EngineExe)) {
  $signatureInfo = Get-AuthenticodeSignature -LiteralPath $item
  if ($signatureInfo.Status -ne 'Valid' -or $null -eq $signatureInfo.TimeStamperCertificate) { throw 'SIGNATURE_INVALID' }
  $machine = Get-PeMachine $item
  if ($machine -ne '0x8664' -and $item -ne $Installer) { throw 'EXECUTABLE_X64_REQUIRED' }
  @{ fileName=[System.IO.Path]::GetFileName($item); sha256=(Get-FileHash -LiteralPath $item -Algorithm SHA256).Hash;
     machine=$machine; status=$signatureInfo.Status.ToString();
     signer=$signatureInfo.SignerCertificate.Subject;
     timestampSigner=$signatureInfo.TimeStamperCertificate.Subject;
     productVersion=(Get-Item -LiteralPath $item).VersionInfo.ProductVersion }
}
$records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $NewOutputDirectory 'artifacts.json')
'Metadata only. SDK signtool /pa /all, installation, DPAPI and all native scenarios remain separate.' |
  Set-Content -LiteralPath (Join-Path $NewOutputDirectory 'scope.txt')
