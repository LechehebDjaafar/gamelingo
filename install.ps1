# Install GameLingo skills into %USERPROFILE%\.claude\skills (Windows, PowerShell)
$ErrorActionPreference = "Stop"
$dest = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $env:USERPROFILE ".claude\skills" }
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Get-ChildItem -Directory (Join-Path $here "skills") | ForEach-Object {
    $target = Join-Path $dest $_.Name
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse $_.FullName $target
    Write-Host "installed: $($_.Name)"
}
Write-Host "Done. Restart Claude Code, then try: /gamelingo"
Write-Host "Optional (Arabic/RTL): python -m pip install -r `"$here\requirements-rtl.txt`""
