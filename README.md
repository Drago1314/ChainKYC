# ⬡ ChainKYC — Blockchain-based Secure KYC Verification System

![Ethereum](https://img.shields.io/badge/Ethereum-3C3C3D?style=for-the-badge&logo=Ethereum&logoColor=white) ![Solidity](https://img.shields.io/badge/Solidity-%23363636.svg?style=for-the-badge&logo=solidity&logoColor=white) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)

> **6th Semester Mini Project** · Blockchain Technology · BE Computer Engineering  
> Mumbai University · Academic Year 2025–26

**Team:**
- Miqdaad Sayyed — Frontend & Integration
- Arfat Shaikh — Smart Contract & Backend
- Faazil Mirza Shaikh — Blockchain Dev

---

## 📌 Project Overview

ChainKYC is a decentralized KYC (Know Your Customer) verification system built on the Ethereum blockchain. It solves the core problem with traditional KYC — centralized storage, data breach risk, and no user control — by storing only **document hashes on-chain** while keeping actual documents privately on **IPFS**.

### Key Features
- 🔒 SHA-256 document hashes stored immutably on Ethereum
- 🔐 Actual documents stored encrypted on IPFS (off-chain)
- ⚡ Smart contract enforces verification logic (no centralized server)
- 🌐 Role-based access: Owner → Verifiers → Users
- 👁️ Full on-chain audit trail via Solidity events
- 🦊 MetaMask / WalletConnect integration

---

## 🚀 Quick Start (One-Click)

### Just Run the Frontend
```
Double-click START.bat
```
That's it! The batch file will:
1. Start a local Python HTTP server (if Python is available)
2. Open `http://localhost:8000/index.html` in your browser
3. If Python isn't found, it opens `index.html` directly

### Demo Credentials
| Portal     | Credential       |
|------------|-----------------|
| Verifier   | `verifier123`   |
| User KYC   | Connect any wallet (simulated) |

---

## 📦 Portability — Run on Any PC

### Create a Portable ZIP
```
Double-click MAKE_PORTABLE.bat
```
This creates `ChainKYC_Portable_DDMMYY.zip` in the parent directory, excluding:
- `node_modules/` (large, reinstalled via setup)
- `.env` (contains private keys — NEVER share this)
- `cache/` and `artifacts/` (regenerated on compile)

### On the Target PC
1. Extract the ZIP
2. Double-click `START.bat` to run the frontend
3. (Optional) Run `SETUP_AND_DEPLOY.bat` to set up Hardhat + deploy

**Requirements for target PC:**
- A modern web browser (Chrome/Firefox/Edge)
- Python 3 (optional, for local server — download from https://python.org)
- Node.js v16+ (only if deploying — download from https://nodejs.org)

---

## 🔗 Smart Contract Deployment

### Full Automated Setup + Deploy
```
Double-click SETUP_AND_DEPLOY.bat
```
This runs `setup_deploy.py` which handles everything:
1. Checks Node.js is installed
2. Creates a Hardhat project in `./chainkyc-hardhat/`
3. Installs npm dependencies
4. Compiles `KYCVerification.sol`
5. Runs test suite
6. Prompts for `.env` credentials (private key, RPC URL)
7. Deploys to Sepolia testnet
8. Auto-patches `index.html` with the real contract address + ABI

### Manual Setup (Advanced)
```bash
python setup_deploy.py --setup     # Setup only (no deploy)
python setup_deploy.py --compile   # Compile only
python setup_deploy.py --test      # Run tests
python setup_deploy.py --deploy    # Deploy only (setup must be done)
```

### Prerequisites for Deployment
1. **MetaMask wallet** with Sepolia ETH
   - Get free Sepolia ETH: https://sepoliafaucet.com
2. **Alchemy RPC URL** (free)
   - Sign up: https://www.alchemy.com → New App → Ethereum → Sepolia
3. **Etherscan API key** (optional, for contract verification)
   - Get free key: https://etherscan.io/myapikey

---

## 🗂️ Project Structure

```
files for real real/
├── START.bat                 ← One-click launch (opens frontend in browser)
├── SETUP_AND_DEPLOY.bat      ← One-click Hardhat setup + Sepolia deploy
├── MAKE_PORTABLE.bat         ← Creates portable ZIP for sharing
├── index.html                ← Frontend DApp (React 18 + Babel, no build step)
├── KYCVerification.sol       ← Ethereum smart contract (Solidity 0.8.19)
├── setup_deploy.py           ← Python automation script
├── README.md                 ← This file
└── chainkyc-hardhat/         ← Hardhat project (created by setup_deploy.py)
    ├── contracts/KYCVerification.sol
    ├── scripts/deploy.js
    ├── test/KYCVerification.test.js
    ├── hardhat.config.js
    ├── package.json
    ├── .env.example
    └── deployments/sepolia.json
```

---

## 📊 Smart Contract — Function Reference

| Function | Access | Description |
|---|---|---|
| `submitKYC(hash, cid, aadhaar, pan, name)` | Any user | Submit KYC with document hash |
| `approveKYC(user, note)` | Verifier | Approve a pending KYC |
| `rejectKYC(user, reason)` | Verifier | Reject with reason |
| `revokeKYC(user, reason)` | Owner | Revoke an approved KYC |
| `addVerifier(address)` | Owner | Whitelist a verifier |
| `removeVerifier(address)` | Owner | Remove verifier |
| `getKYCStatus(user)` | Public | Get status enum (0–4) |
| `isKYCVerified(user)` | Public | Quick boolean check |
| `getMyKYCRecord()` | Authenticated user | Get own full record |
| `getKYCRecord(user)` | Owner / Verifier | Get any user's full record |
| `verifyDocumentIntegrity(user, hash)` | Public | Compare hash for integrity |
| `getStats()` | Public | Platform-wide statistics |
| `getKYCUsers(offset, limit)` | Owner / Verifier | Paginated user listing |
| `transferOwnership(newOwner)` | Owner | Transfer ownership (emits event) |

### KYC Status Enum
```
0 = NONE       (no record)
1 = SUBMITTED  (pending review)
2 = APPROVED   (verified)
3 = REJECTED   (rejected, can resubmit)
4 = REVOKED    (previously approved, now revoked)
```

---

## 🔧 Web3 Integration

Once deployed, the contract address and ABI are auto-injected into `index.html`:

```javascript
const CONTRACT_ADDRESS = "0xYOUR_DEPLOYED_CONTRACT_ADDRESS";
const CONTRACT_ABI     = [...]; // Full ABI auto-generated

// Connect with ethers.js
const provider = new ethers.BrowserProvider(window.ethereum);
const signer   = await provider.getSigner();
const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

// Submit KYC
const docHash = ethers.keccak256(ethers.toUtf8Bytes(documentContent));
const tx = await contract.submitKYC(docHash, ipfsCID, maskedAadhaar, pan, fullName);
await tx.wait();
```

---

## 🧪 Test Cases

The test suite covers:
- ✅ Deployment & ownership
- ✅ KYC submission & event emission
- ✅ Duplicate submission rejection
- ✅ Re-submission after rejection
- ✅ Verifier approval & rejection
- ✅ Non-verifier access control
- ✅ Document integrity verification
- ✅ Verifier management (add/remove)
- ✅ KYC revocation
- ✅ Stats counter tracking

```bash
# Run tests
python setup_deploy.py --test

# Or directly via Hardhat
cd chainkyc-hardhat && npx hardhat test
```

---

## 📚 Tech Stack

| Layer | Technology |
|---|---|
| Smart Contract | Solidity 0.8.19, Ethereum |
| Development | Hardhat 2.22+ |
| Frontend | React 18 (CDN), Babel (in-browser transpilation) |
| Wallet | MetaMask, WalletConnect |
| Storage | IPFS (via Pinata) |
| Testnet | Ethereum Sepolia |
| Hashing | SHA-256 (client-side via SubtleCrypto API) |
| Automation | Python 3 (setup_deploy.py) |

---

## 📄 References

1. Ethereum Documentation — https://ethereum.org/en/developers/docs/
2. Solidity Documentation — https://docs.soliditylang.org/
3. IPFS Documentation — https://docs.ipfs.tech/
4. MetaMask Developer Docs — https://docs.metamask.io/
5. Hardhat Documentation — https://hardhat.org/docs
6. Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System.
7. Buterin, V. (2014). Ethereum Whitepaper.

---

*Submitted in partial fulfillment of the requirements for BE Computer Engineering,*  
*Blockchain Technology Subject, Mumbai University, 2025–26.*
