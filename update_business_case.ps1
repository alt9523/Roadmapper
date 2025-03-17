# Load the JSON file
$json = Get-Content 'roadmap.json' -Raw | ConvertFrom-Json

# Update P3's business case
$json.products[2].businessCase = @{
    'Save schedule' = $true
    'Save hardware costs' = $true
    'Relieve supply chain constraints' = $true
    'Increase Pwin by hitting PTW' = $false
    'Reduce specialty training' = $false
    'Save weight' = $true
    'Increase performance' = $true
    'Unify parts' = $false
    'Quickly iterate design/EMs' = $false
    'Agility in Design and AI&T' = $false
    'Digital Spares' = $false
}

# Update P4's business case
$json.products[3].businessCase = @{
    'Save schedule' = $false
    'Save hardware costs' = $true
    'Relieve supply chain constraints' = $true
    'Increase Pwin by hitting PTW' = $false
    'Reduce specialty training' = $false
    'Save weight' = $true
    'Increase performance' = $true
    'Unify parts' = $true
    'Quickly iterate design/EMs' = $false
    'Agility in Design and AI&T' = $true
    'Digital Spares' = $false
}

# Check for more products and update them if needed
for ($i = 4; $i -lt $json.products.Length; $i++) {
    $product = $json.products[$i]
    # Check if the business case has the old format
    if ($product.businessCase -and (-not $product.businessCase.'Save schedule') -and (-not $product.businessCase.'Save hardware costs')) {
        Write-Host "Updating business case for product $($product.id): $($product.name)"
        # Set some random values for demonstration
        $product.businessCase = @{
            'Save schedule' = (Get-Random -InputObject @($true, $false))
            'Save hardware costs' = (Get-Random -InputObject @($true, $false))
            'Relieve supply chain constraints' = (Get-Random -InputObject @($true, $false))
            'Increase Pwin by hitting PTW' = (Get-Random -InputObject @($true, $false))
            'Reduce specialty training' = (Get-Random -InputObject @($true, $false))
            'Save weight' = (Get-Random -InputObject @($true, $false))
            'Increase performance' = (Get-Random -InputObject @($true, $false))
            'Unify parts' = (Get-Random -InputObject @($true, $false))
            'Quickly iterate design/EMs' = (Get-Random -InputObject @($true, $false))
            'Agility in Design and AI&T' = (Get-Random -InputObject @($true, $false))
            'Digital Spares' = (Get-Random -InputObject @($true, $false))
        }
    }
}

# Save the updated JSON file
$json | ConvertTo-Json -Depth 20 | Set-Content 'roadmap.json'
Write-Host "Business case formats updated successfully!" 