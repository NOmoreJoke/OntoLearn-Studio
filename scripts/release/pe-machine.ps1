# Pure bounded PE-header reader; no signing, installation, process launch or package provenance claim.
function Get-PeMachine([string]$FilePath) {
  $stream = $null
  $reader = $null
  try {
    # Deny new write/delete opens for this handle on Windows. This does not authenticate the caller's path.
    $stream = [System.IO.File]::Open($FilePath, [System.IO.FileMode]::Open,
      [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $length = $stream.Length
    if ($length -lt 64) { throw 'PE_DOS_BOUNDS' }
    $reader = [System.IO.BinaryReader]::new($stream)
    if ($reader.ReadUInt16() -ne 0x5a4d) { throw 'PE_MZ_REQUIRED' }
    $stream.Position = 0x3c
    $offset = [long]$reader.ReadUInt32()
    if ($offset -lt 64 -or $offset -gt $length - 6) { throw 'PE_HEADER_BOUNDS' }
    $stream.Position = $offset
    if ($reader.ReadUInt32() -ne 0x00004550) { throw 'PE_SIGNATURE_REQUIRED' }
    $machine = $reader.ReadUInt16()
    if ($stream.Length -ne $length) { throw 'PE_SIZE_CHANGED' }
    return ('0x{0:x4}' -f $machine)
  } catch {
    # No original exception/path escapes to the collector's fixed error surface.
    throw 'PE_INVALID'
  } finally {
    if ($null -ne $reader) { $reader.Dispose() }
    if ($null -ne $stream) { $stream.Dispose() }
  }
}
