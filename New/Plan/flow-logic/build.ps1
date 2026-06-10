$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
$requiredImages = @(
  "images/cbm-flow-dual-path.png","images/cbm-flow-cursor-sequence.png","images/cbm-flow-agent-sequence.png",
  "images/cbm-flow-element-index.png","images/cbm-flow-agent-decisions.png","images/cbm-flow-error-handling.png",
  "images/cbm-flow-provider-switch.png","images/cbm-flow-migration.png"
)
foreach ($img in $requiredImages) { if (-not (Test-Path $img)) { Write-Host "ERROR: Missing $img"; exit 1 } }
pdflatex -interaction=nonstopmode browser-flow-framework.tex | Out-Null
pdflatex -interaction=nonstopmode browser-flow-framework.tex | Out-Null
if (Test-Path "browser-flow-framework.pdf") { Write-Host "Success: browser-flow-framework.pdf" } else { exit 1 }
