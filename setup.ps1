# Setup script for MCP Python Server

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "CV Generator MCP Server (Python) - Setup" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check Python installation
Write-Host "`n[1/4] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check pip
Write-Host "`n[2/4] Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ pip installed: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ pip not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n[3/4] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check environment file
Write-Host "`n[4/4] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Using default values." -ForegroundColor Yellow
    Write-Host "   Please create .env with your MongoDB URI" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Update .env with your MongoDB URI" -ForegroundColor White
Write-Host "   2. Start the server: python server.py" -ForegroundColor White
Write-Host "   3. Test the client: python client.py" -ForegroundColor White
Write-Host "   4. Configure Claude Desktop (see README.md)" -ForegroundColor White

Write-Host "`n📚 Documentation:" -ForegroundColor Cyan
Write-Host "   • README.md - Complete guide" -ForegroundColor White
Write-Host "   • server.py - MCP server implementation" -ForegroundColor White
Write-Host "   • client.py - Test client" -ForegroundColor White

Write-Host "`n🚀 Quick Start:" -ForegroundColor Cyan
Write-Host "   python server.py" -ForegroundColor Yellow

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
