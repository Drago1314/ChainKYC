@echo off
title ChainKYC - Setup & Deploy
color 0B

echo.
echo  ===============================================
echo   ChainKYC - Hardhat Setup ^& Sepolia Deployment
echo  ===============================================
echo.
echo  This will:
echo    1. Check prerequisites (Node.js, Python)
echo    2. Create Hardhat project structure
echo    3. Install npm dependencies (~2 min)
echo    4. Compile KYCVerification.sol
echo    5. Run tests
echo    6. Ask for your .env credentials
echo    7. Deploy to Sepolia testnet
echo    8. Auto-patch index.html with contract address
echo.
echo  REQUIREMENTS:
echo    - Node.js v16+ (https://nodejs.org)
echo    - Python 3   (https://python.org)
echo    - MetaMask wallet with Sepolia ETH
echo    - Alchemy RPC URL (free: https://alchemy.com)
echo.

set /p CONFIRM="  Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo  Cancelled.
    pause
    exit /b
)

echo.
echo  Starting setup_deploy.py...
echo.

python setup_deploy.py

echo.
echo  ===============================================
echo   Done! You can now run START.bat to launch.
echo  ===============================================
echo.
pause
