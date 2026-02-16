# Quick script to check document count
Write-Host "Checking documents.json..." -ForegroundColor Cyan

if (Test-Path "documents.json") {
    $content = Get-Content "documents.json" -Raw | ConvertFrom-Json
    $count = ($content.PSObject.Properties | Measure-Object).Count
    
    Write-Host "`n✅ documents.json found!" -ForegroundColor Green
    Write-Host "📊 Total documents: $count" -ForegroundColor Yellow
    
    if ($count -ge 500 -and $count -le 1000) {
        Write-Host "✅ SUCCESS: Within target range (500-1000)" -ForegroundColor Green
    } elseif ($count -gt 1000) {
        Write-Host "✅ SUCCESS: Exceeds minimum (500+)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: Below target (expected 500-1000)" -ForegroundColor Yellow
    }
    
    # Show sample document IDs
    Write-Host "`n📄 Sample document IDs:" -ForegroundColor Cyan
    $sampleIds = $content.PSObject.Properties.Name | Select-Object -First 10
    foreach ($id in $sampleIds) {
        Write-Host "  - $id" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ documents.json not found!" -ForegroundColor Red
    Write-Host "Run: python scripts/test_public_datasets.py" -ForegroundColor Yellow
    Write-Host "Or start the server to generate it automatically." -ForegroundColor Yellow
}
