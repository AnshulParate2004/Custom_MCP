$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
$requiredImages = @(
  "images/cbm-tech-platform-architecture.png","images/cbm-mcp-tool-data-flow.png","images/cbm-page-state-pipeline.png",
  "images/cbm-langgraph-react-agent.png","images/cbm-litellm-providers.png","images/cbm-session-lifecycle.png",
  "images/cbm-package-layout.png","images/cbm-mcp-deployment.png"
)
foreach ($img in $requiredImages) { if (-not (Test-Path $img)) { Write-Host "ERROR: Missing $img"; exit 1 } }
Write-Host "Building tech-plan.pdf..."
pdflatex -interaction=nonstopmode tech-plan.tex | Out-Null
pdflatex -interaction=nonstopmode tech-plan.tex | Out-Null
if (Test-Path "tech-plan.pdf") { Write-Host "Success: tech-plan.pdf" } else { Write-Host "FAILED"; Get-Content tech-plan.log -Tail 30; exit 1 }
