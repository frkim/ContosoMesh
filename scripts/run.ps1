# ContosoMesh Run Script for Windows
# This script starts the ContosoMesh application

Write-Host "🏠 Starting ContosoMesh Application" -ForegroundColor Blue
Write-Host "===================================" -ForegroundColor Blue

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn; print('Dependencies OK')" 2>$null
    Write-Host "✅ Dependencies verified" -ForegroundColor Green
} catch {
    Write-Host "❌ Dependencies missing. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Start the application
Write-Host ""
Write-Host "🚀 Starting ContosoMesh server..." -ForegroundColor Green
Write-Host "   Server will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "   API documentation at: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Change to backend directory and run the server
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload