# PowerShell script pour tester la connexion PostgreSQL à Dremio

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Test de connexion PostgreSQL à Dremio" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Attendre que Dremio soit prêt
Write-Host "`nAttente du démarrage de Dremio..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test 1: Vérifier que le port 31010 est ouvert
Write-Host "`nTest 1: Vérification du port 31010..." -ForegroundColor Yellow
try {
    $tcpConnection = Test-NetConnection -ComputerName localhost -Port 31010 -WarningAction SilentlyContinue
    if ($tcpConnection.TcpTestSucceeded) {
        Write-Host "✓ Port 31010 est accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ Port 31010 n'est pas accessible" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Erreur lors du test du port 31010" -ForegroundColor Red
    exit 1
}

# Test 2: Tester avec Python psycopg2
Write-Host "`nTest 2: Connexion avec Python psycopg2..." -ForegroundColor Yellow
$pythonScript = @"
try:
    import psycopg2
    conn = psycopg2.connect(
        host='localhost',
        port=31010,
        user='dremio_user',
        password='dremio_password',
        database='dremio'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print('✓ Connexion Python réussie')
    print(f'Version: {version}')
    cursor.close()
    conn.close()
except ImportError:
    print('! psycopg2 n est pas installé. Installer avec: pip install psycopg2-binary')
except Exception as e:
    print(f'✗ Erreur de connexion: {e}')
    print('Note: Il faut d abord créer un utilisateur dans Dremio UI')
"@

python -c $pythonScript

# Test 3: Vérifier l'UI Dremio
Write-Host "`nTest 3: Vérification de l'UI Dremio..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9047" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ UI Dremio accessible sur http://localhost:9047" -ForegroundColor Green
} catch {
    Write-Host "✗ UI Dremio non accessible" -ForegroundColor Red
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Tests terminés!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`nProchaines étapes:"
Write-Host "1. Accéder à http://localhost:9047"
Write-Host "2. Créer un utilisateur admin"
Write-Host "3. Créer un utilisateur 'dremio_user' avec mot de passe 'dremio_password'"
Write-Host "4. Exécuter le script setup.sql pour créer les données d'exemple"
