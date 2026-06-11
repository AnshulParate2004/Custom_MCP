# One-command setup for Custom MCP Browser Automation
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Custom MCP Browser Setup ===" -ForegroundColor Cyan

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: uv not found. Install from https://docs.astral.sh/uv/" -ForegroundColor Red
    exit 1
}

Write-Host "Installing Python dependencies..."
uv sync --extra test

Write-Host "Installing Playwright Chromium..."
uv run python -m playwright install chromium

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — add your API keys" -ForegroundColor Yellow
}

Write-Host "Running tests..."
uv run pytest tests/ -v --tb=short

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "1. Edit .env with OPENAI_API_KEY (or other provider key)"
Write-Host "2. Copy cursor-mcp.example.json into Cursor MCP settings"
Write-Host "   Path: D:/Custom_MCP/New/Implement"
Write-Host "3. Enable Browser_Automation and/or Browser_Agent MCP servers"
