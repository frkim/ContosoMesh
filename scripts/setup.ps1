# ContosoMesh Setup Script for Windows
# This script sets up the ContosoMesh demo environment

Write-Host "🏠 ContosoMesh Setup Script" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue

# Check if Python is installed
Write-Host "📦 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11 or later." -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Python version
$pythonVersionNum = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$pythonVersionNum -lt [version]"3.11") {
    Write-Host "❌ Python 3.11 or later required. Found: $pythonVersionNum" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "🔧 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green

# Create .env file if it doesn't exist
Write-Host "🔧 Setting up environment variables..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    @"
# ContosoMesh Environment Variables
# Azure AI Search (Optional - demo will work with mock data)
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-key

# Azure OpenAI (Optional - for advanced reasoning)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Database
DATABASE_PATH=contoso_mesh.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env file created. Please update with your Azure credentials if available." -ForegroundColor Green
} else {
    Write-Host "   .env file already exists" -ForegroundColor Yellow
}

# Initialize database
Write-Host "🗄️ Initializing database..." -ForegroundColor Yellow
python -c "
from backend.database.db import Database
from backend.search.azure_search import AzureSearchService

# Initialize database and search
db = Database()
search = AzureSearchService()

# Index products
products = db.get_products()
search.index_products(products)

print('Database and search index initialized successfully')
"

Write-Host "✅ Database initialized" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Blue
Write-Host "   1. Update .env file with your Azure credentials (optional)" -ForegroundColor White
Write-Host "   2. Run the application with: .\scripts\run.ps1" -ForegroundColor White
Write-Host "   3. Open your browser to: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Available endpoints:" -ForegroundColor Blue
Write-Host "   • Frontend:      http://localhost:8000" -ForegroundColor White
Write-Host "   • API Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Health Check:  http://localhost:8000/api/health" -ForegroundColor White
Write-Host ""
Write-Host "🤖 Features:" -ForegroundColor Blue
Write-Host "   • Multi-agent order processing" -ForegroundColor White
Write-Host "   • Real-time agent activity logging" -ForegroundColor White
Write-Host "   • Product catalog with search" -ForegroundColor White
Write-Host "   • Warehouse management" -ForegroundColor White
Write-Host "   • Order tracking" -ForegroundColor White