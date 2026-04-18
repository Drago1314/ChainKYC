#!/usr/bin/env python3
"""
ChainKYC — Automated Hardhat Setup & Deployment Script
======================================================
Team: Miqdaad Sayyed | Arfat Shaikh | Faazil Mirza Shaikh
6th Sem BT Mini Project — Mumbai University — 2025-26

What this script does:
  1. Checks Node.js is installed
  2. Creates a clean Hardhat project in ./chainkyc-hardhat/
  3. Writes all required config, contract, deploy, and test files
  4. Installs all npm dependencies
  5. Compiles the smart contract
  6. Guides you through getting Sepolia ETH and setting up .env
  7. Deploys the contract to Sepolia testnet
  8. Automatically patches index.html with the real contract address + ABI

Usage:
  python3 setup_deploy.py             # Full setup + deploy
  python3 setup_deploy.py --setup     # Setup only (no deploy)
  python3 setup_deploy.py --compile   # Compile only
  python3 setup_deploy.py --deploy    # Deploy only (setup must be done)
  python3 setup_deploy.py --test      # Run tests
"""

import os, sys, subprocess, json, shutil, textwrap, argparse, time
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
COLORS = {
    'green':  '\033[92m', 'yellow': '\033[93m', 'red':    '\033[91m',
    'blue':   '\033[94m', 'cyan':   '\033[96m', 'bold':   '\033[1m',
    'reset':  '\033[0m',
}
def c(text, color): return COLORS.get(color,'') + str(text) + COLORS['reset']
def ok(msg):    print(c('  ✓  ', 'green')  + msg)
def info(msg):  print(c('  ℹ  ', 'cyan')   + msg)
def warn(msg):  print(c('  ⚠  ', 'yellow') + msg)
def err(msg):   print(c('  ✕  ', 'red')    + msg)
def step(msg):  print('\n' + c('▸ ' + msg, 'bold'))
def hr():       print(c('─' * 60, 'blue'))

PROJECT_DIR = Path('./chainkyc-hardhat')
HTML_FILE   = Path('./index.html')    # update this path if your HTML is elsewhere

# ──────────────────────────────────────────────────────────────────────────────
def run(cmd, cwd=None, capture=False):
    """Run a shell command, raise on failure."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or PROJECT_DIR,
        capture_output=capture, text=True
    )
    if result.returncode != 0:
        err_text = result.stderr or result.stdout or '(no output)'
        raise RuntimeError(f'Command failed: {cmd}\n{err_text}')
    return result.stdout if capture else None

# ──────────────────────────────────────────────────────────────────────────────
def check_node():
    step('Checking prerequisites')
    # Node.js
    try:
        v = subprocess.check_output('node --version', shell=True, text=True).strip()
        ok(f'Node.js {v} found')
    except Exception:
        err('Node.js not found. Install from https://nodejs.org (v18+ recommended)')
        sys.exit(1)
    major = int(v.lstrip('v').split('.')[0])
    if major < 16:
        err(f'Node.js v{major} is too old. Need v16+. Please upgrade.')
        sys.exit(1)
    # npm
    try:
        npm_v = subprocess.check_output('npm --version', shell=True, text=True).strip()
        ok(f'npm {npm_v} found')
    except Exception:
        err('npm not found. It should come with Node.js. Reinstall Node.js.')
        sys.exit(1)

# ──────────────────────────────────────────────────────────────────────────────
def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip('\n'), encoding='utf-8')

# ──────────────────────────────────────────────────────────────────────────────
def setup_project():
    step('Setting up Hardhat project')

    if PROJECT_DIR.exists():
        warn(f'Directory {PROJECT_DIR} already exists. Skipping directory creation.')
    else:
        PROJECT_DIR.mkdir(parents=True)
        ok(f'Created {PROJECT_DIR}')

    # ── package.json ──────────────────────────────────────────────────────────
    pkg = {
        "name": "chainkyc",
        "version": "1.0.0",
        "description": "Blockchain-based Secure KYC Verification System",
        "scripts": {
            "compile": "npx hardhat compile",
            "test":    "npx hardhat test",
            "deploy":  "npx hardhat run scripts/deploy.js --network sepolia",
            "deploy:local": "npx hardhat run scripts/deploy.js --network localhost",
            "node":    "npx hardhat node"
        },
        "devDependencies": {
            "hardhat":                              "^2.22.3",
            "@nomicfoundation/hardhat-toolbox":     "^5.0.0",
            "@nomicfoundation/hardhat-ethers":      "^3.0.6",
            "ethers":                               "^6.12.1",
            "dotenv":                               "^16.4.5",
            "chai":                                 "^4.4.1"
        }
    }
    (PROJECT_DIR / 'package.json').write_text(json.dumps(pkg, indent=2), encoding='utf-8')
    ok('package.json written')

    # ── hardhat.config.js ─────────────────────────────────────────────────────
    write_file(PROJECT_DIR / 'hardhat.config.js', '''
        require("@nomicfoundation/hardhat-toolbox");
        require("dotenv").config();

        // Pull values from .env
        const PRIVATE_KEY  = process.env.PRIVATE_KEY  || "0x" + "0".repeat(64);  // fallback for compile
        const SEPOLIA_RPC   = process.env.SEPOLIA_RPC  || "";
        const ETHERSCAN_KEY = process.env.ETHERSCAN_KEY || "";

        /** @type import('hardhat/config').HardhatUserConfig */
        module.exports = {
          solidity: {
            version: "0.8.19",
            settings: {
              optimizer: { enabled: true, runs: 200 }
            }
          },
          networks: {
            // Local Hardhat node (for testing without real ETH)
            localhost: {
              url: "http://127.0.0.1:8545"
            },
            // Sepolia testnet (for real deployment)
            sepolia: {
              url: SEPOLIA_RPC,
              accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
              chainId: 11155111,
              gasPrice: "auto"
            }
          },
          etherscan: {
            apiKey: ETHERSCAN_KEY   // for contract verification on Etherscan
          },
          paths: {
            sources:   "./contracts",
            tests:     "./test",
            cache:     "./cache",
            artifacts: "./artifacts"
          }
        };
    ''')
    ok('hardhat.config.js written')

    # ── .env.example ─────────────────────────────────────────────────────────
    write_file(PROJECT_DIR / '.env.example', '''
        # ── ChainKYC Environment Variables ──────────────────────────────────
        # Copy this file to .env and fill in your values.
        # NEVER commit .env to git — it contains your private key!

        # Your deployer wallet's private key (from MetaMask: Account Details → Export Private Key)
        # Must start with 0x
        PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE

        # Sepolia RPC URL — get a free one from:
        #   Alchemy:  https://www.alchemy.com  (recommended, free tier)
        #   Infura:   https://infura.io
        SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY

        # Etherscan API key for contract verification (optional but recommended)
        # Get free key at: https://etherscan.io/myapikey
        ETHERSCAN_KEY=YOUR_ETHERSCAN_API_KEY
    ''')
    ok('.env.example written')

    # ── .gitignore ────────────────────────────────────────────────────────────
    write_file(PROJECT_DIR / '.gitignore', '''
        node_modules/
        artifacts/
        cache/
        .env
        deployments/
        *.log
    ''')
    ok('.gitignore written')

    # ── Smart Contract ────────────────────────────────────────────────────────
    contract_src = Path(__file__).parent / 'KYCVerification.sol'
    contract_dst = PROJECT_DIR / 'contracts' / 'KYCVerification.sol'
    contract_dst.parent.mkdir(parents=True, exist_ok=True)

    if contract_src.exists():
        shutil.copy(contract_src, contract_dst)
        ok(f'KYCVerification.sol copied from {contract_src}')
    else:
        # Inline the contract if the file isn't next to this script
        warn('KYCVerification.sol not found next to this script. Writing inline copy.')
        write_file(contract_dst, INLINE_CONTRACT)
        ok('KYCVerification.sol written (inline)')

    # ── Deploy Script ─────────────────────────────────────────────────────────
    write_file(PROJECT_DIR / 'scripts' / 'deploy.js', '''
        const hre = require("hardhat");
        const fs  = require("fs");
        const path = require("path");

        async function main() {
          console.log("\\n🔗 ChainKYC — Deploying to:", hre.network.name);
          console.log("─".repeat(50));

          // Get deployer account
          const [deployer] = await hre.ethers.getSigners();
          console.log("Deployer address :", deployer.address);

          const balance = await hre.ethers.provider.getBalance(deployer.address);
          console.log("Deployer balance :", hre.ethers.formatEther(balance), "ETH");

          if (hre.network.name === "sepolia" && balance < hre.ethers.parseEther("0.01")) {
            console.error("\\n⚠  Low balance! You need at least 0.01 ETH on Sepolia to deploy.");
            console.error("   Get free Sepolia ETH from: https://sepoliafaucet.com");
            process.exit(1);
          }

          // Deploy the contract
          console.log("\\nDeploying KYCVerification...");
          const KYCVerification = await hre.ethers.getContractFactory("KYCVerification");
          const kyc = await KYCVerification.deploy();
          await kyc.waitForDeployment();

          const contractAddress = await kyc.getAddress();
          const deployTx        = kyc.deploymentTransaction();
          const receipt         = await deployTx.wait();

          console.log("\\n✅ Contract deployed!");
          console.log("─".repeat(50));
          console.log("Contract Address :", contractAddress);
          console.log("Tx Hash          :", receipt.hash);
          console.log("Block Number     :", receipt.blockNumber);
          console.log("Gas Used         :", receipt.gasUsed.toString());
          console.log("Network          :", hre.network.name);

          // Save deployment info to JSON
          const deploymentsDir = path.join(__dirname, "../deployments");
          if (!fs.existsSync(deploymentsDir)) fs.mkdirSync(deploymentsDir, { recursive: true });

          const deployInfo = {
            network:         hre.network.name,
            contractAddress: contractAddress,
            deployer:        deployer.address,
            txHash:          receipt.hash,
            blockNumber:     receipt.blockNumber,
            timestamp:       new Date().toISOString(),
            abi:             JSON.parse(fs.readFileSync(
              path.join(__dirname, "../artifacts/contracts/KYCVerification.sol/KYCVerification.json")
            )).abi
          };

          const outFile = path.join(deploymentsDir, `${hre.network.name}.json`);
          fs.writeFileSync(outFile, JSON.stringify(deployInfo, null, 2));
          console.log("\\nDeployment info saved to:", outFile);

          // Etherscan link
          if (hre.network.name === "sepolia") {
            console.log("\\nView on Etherscan:");
            console.log(`  https://sepolia.etherscan.io/address/${contractAddress}`);
            console.log("\\n⏳ Waiting 30s before Etherscan verification...");
            await new Promise(r => setTimeout(r, 30000));
            try {
              await hre.run("verify:verify", { address: contractAddress, constructorArguments: [] });
              console.log("✅ Contract verified on Etherscan!");
            } catch(e) {
              console.log("ℹ  Etherscan verification skipped:", e.message);
            }
          }

          console.log("\\n🎉 Deployment complete!");
          return contractAddress;
        }

        main().catch((error) => { console.error(error); process.exitCode = 1; });
    ''')
    ok('scripts/deploy.js written')

    # ── Test File ─────────────────────────────────────────────────────────────
    write_file(PROJECT_DIR / 'test' / 'KYCVerification.test.js', '''
        const { expect }  = require("chai");
        const { ethers }  = require("hardhat");

        describe("KYCVerification", function () {
          let kyc, owner, verifier, user1, user2;
          const DOC_HASH = ethers.keccak256(ethers.toUtf8Bytes("test_document_bundle_v1"));
          const IPFS_CID = "QmTestCIDabcdefghijklmnopqrstuvwxyz1234567890";

          beforeEach(async () => {
            [owner, verifier, user1, user2] = await ethers.getSigners();
            const KYC = await ethers.getContractFactory("KYCVerification");
            kyc = await KYC.deploy();
            await kyc.waitForDeployment();
            await kyc.addVerifier(verifier.address);
          });

          describe("Deployment", () => {
            it("Should set the owner correctly", async () => {
              expect(await kyc.owner()).to.equal(owner.address);
            });
            it("Owner should be a verifier by default", async () => {
              expect(await kyc.isVerifier(owner.address)).to.be.true;
            });
          });

          describe("KYC Submission", () => {
            it("Should allow user to submit KYC", async () => {
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User");
              expect(await kyc.getKYCStatus(user1.address)).to.equal(1); // SUBMITTED
            });
            it("Should emit KYCSubmitted event", async () => {
              await expect(kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User"))
                .to.emit(kyc, "KYCSubmitted")
                .withArgs(user1.address, DOC_HASH, IPFS_CID, await ethers.provider.getBlock("latest").then(b => b.timestamp + 1));
            });
            it("Should reject resubmission when already submitted", async () => {
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User");
              await expect(kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User"))
                .to.be.revertedWith("KYC: record already active for this address");
            });
            it("Should allow resubmission after rejection", async () => {
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User");
              await kyc.connect(verifier).rejectKYC(user1.address, "Blurry scan");
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User Updated");
              expect(await kyc.getKYCStatus(user1.address)).to.equal(1);
            });
          });

          describe("KYC Approval", () => {
            beforeEach(async () => {
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User");
            });
            it("Should allow verifier to approve KYC", async () => {
              await kyc.connect(verifier).approveKYC(user1.address, "All docs OK");
              expect(await kyc.isKYCVerified(user1.address)).to.be.true;
              expect(await kyc.getKYCStatus(user1.address)).to.equal(2); // APPROVED
            });
            it("Should NOT allow non-verifier to approve", async () => {
              await expect(kyc.connect(user2).approveKYC(user1.address, "Docs OK"))
                .to.be.revertedWith("KYC: caller is not a whitelisted verifier");
            });
            it("Should increment totalApproved counter", async () => {
              const before = await kyc.getStats();
              await kyc.connect(verifier).approveKYC(user1.address, "OK");
              const after = await kyc.getStats();
              expect(after[1]).to.equal(before[1] + 1n);
            });
          });

          describe("KYC Rejection", () => {
            beforeEach(async () => {
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User");
            });
            it("Should allow verifier to reject KYC", async () => {
              await kyc.connect(verifier).rejectKYC(user1.address, "PAN card blurry");
              expect(await kyc.getKYCStatus(user1.address)).to.equal(3); // REJECTED
            });
            it("Should require a rejection reason", async () => {
              await expect(kyc.connect(verifier).rejectKYC(user1.address, ""))
                .to.be.revertedWith("KYC: rejection reason cannot be empty");
            });
          });

          describe("Document Integrity", () => {
            it("Should verify correct document hash", async () => {
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User");
              expect(await kyc.verifyDocumentIntegrity(user1.address, DOC_HASH)).to.be.true;
            });
            it("Should reject tampered document hash", async () => {
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User");
              const fakeHash = ethers.keccak256(ethers.toUtf8Bytes("tampered_document"));
              expect(await kyc.verifyDocumentIntegrity(user1.address, fakeHash)).to.be.false;
            });
          });

          describe("Verifier Management", () => {
            it("Owner can add a verifier", async () => {
              await kyc.addVerifier(user2.address);
              expect(await kyc.isVerifier(user2.address)).to.be.true;
            });
            it("Owner can remove a verifier", async () => {
              await kyc.removeVerifier(verifier.address);
              expect(await kyc.isVerifier(verifier.address)).to.be.false;
            });
            it("Non-owner cannot add a verifier", async () => {
              await expect(kyc.connect(user1).addVerifier(user2.address))
                .to.be.revertedWith("KYC: caller is not the owner");
            });
          });

          describe("Revocation", () => {
            it("Owner can revoke an approved KYC", async () => {
              await kyc.connect(user1).submitKYC(DOC_HASH, IPFS_CID, "****-****-1234", "ABCDE1234F", "Test User");
              await kyc.connect(verifier).approveKYC(user1.address, "OK");
              await kyc.revokeKYC(user1.address, "Fraudulent documents detected");
              expect(await kyc.getKYCStatus(user1.address)).to.equal(4); // REVOKED
              expect(await kyc.isKYCVerified(user1.address)).to.be.false;
            });
          });
        });
    ''')
    ok('test/KYCVerification.test.js written')

    ok('Project structure created')


# ──────────────────────────────────────────────────────────────────────────────
def install_deps():
    step('Installing npm dependencies (this takes ~2 minutes)')
    info('Installing: hardhat, ethers, hardhat-toolbox, dotenv, chai...')
    run('npm install', cwd=PROJECT_DIR)
    ok('Dependencies installed')


# ──────────────────────────────────────────────────────────────────────────────
def compile_contract():
    step('Compiling smart contract')
    output = run('npx hardhat compile', cwd=PROJECT_DIR, capture=True)
    if 'compiled' in (output or '').lower() or 'nothing' in (output or '').lower():
        ok('KYCVerification.sol compiled successfully')
    else:
        ok('Compilation done')
        if output: info(output.strip())


# ──────────────────────────────────────────────────────────────────────────────
def run_tests():
    step('Running test suite')
    try:
        result = subprocess.run(
            'npx hardhat test', shell=True, cwd=PROJECT_DIR,
            capture_output=False, text=True
        )
        if result.returncode == 0:
            ok('All tests passed')
        else:
            warn('Some tests failed — check output above')
    except Exception as e:
        err(f'Test run failed: {e}')


# ──────────────────────────────────────────────────────────────────────────────
def setup_env():
    step('Setting up environment variables')
    env_file = PROJECT_DIR / '.env'

    if env_file.exists():
        info('.env already exists — skipping')
        return

    hr()
    print(c('\n  Before deploying, you need:', 'bold'))
    print()
    print('  1. Your wallet PRIVATE KEY (from MetaMask)')
    print('     MetaMask → Account → ⋮ → Account Details → Export Private Key')
    print()
    print('  2. A Sepolia RPC URL (free from Alchemy)')
    print('     → Go to https://www.alchemy.com')
    print('     → Create account → New App → Ethereum → Sepolia')
    print('     → Copy the HTTPS URL')
    print()
    print('  3. Some Sepolia test ETH (free)')
    print('     → Go to https://sepoliafaucet.com')
    print('     → Paste your wallet address and claim 0.5 ETH')
    print()
    hr()

    private_key = input(c('\n  Enter your PRIVATE KEY (0x...): ', 'yellow')).strip()
    sepolia_rpc = input(c('  Enter your Sepolia RPC URL: ', 'yellow')).strip()
    etherscan   = input(c('  Enter your Etherscan API key (or press Enter to skip): ', 'yellow')).strip()

    if not private_key.startswith('0x'):
        private_key = '0x' + private_key

    env_content = f"PRIVATE_KEY={private_key}\nSEPOLIA_RPC={sepolia_rpc}\n"
    if etherscan:
        env_content += f"ETHERSCAN_KEY={etherscan}\n"

    env_file.write_text(env_content, encoding='utf-8')
    ok('.env file created')
    warn('NEVER commit your .env file to git!')


# ──────────────────────────────────────────────────────────────────────────────
def deploy():
    step('Deploying KYCVerification to Sepolia Testnet')

    env_file = PROJECT_DIR / '.env'
    if not env_file.exists():
        err('.env not found. Run with --setup first, or create .env manually.')
        sys.exit(1)

    # Run deploy
    result = subprocess.run(
        'npx hardhat run scripts/deploy.js --network sepolia',
        shell=True, cwd=PROJECT_DIR, capture_output=False, text=True
    )

    if result.returncode != 0:
        err('Deployment failed. Check output above.')
        sys.exit(1)

    # Read deployment info
    deploy_file = PROJECT_DIR / 'deployments' / 'sepolia.json'
    if not deploy_file.exists():
        warn('Deployment JSON not found — skipping HTML patching')
        return

    with open(deploy_file, 'r') as f:
        deploy_data = json.load(f)

    contract_address = deploy_data['contractAddress']
    abi              = deploy_data['abi']

    ok(f'Deployed at: {contract_address}')
    patch_html(contract_address, abi)


# ──────────────────────────────────────────────────────────────────────────────
def patch_html(contract_address: str, abi: list):
    """Patch index.html to inject the real contract address and ABI."""
    step('Patching index.html with contract address + ABI')

    # Look for index.html in various places
    candidates = [
        HTML_FILE,
        Path('./chainkyc/index.html'),
        Path('../index.html'),
        Path('./index.html'),
    ]
    html_path = None
    for c_path in candidates:
        if c_path.exists():
            html_path = c_path
            break

    if not html_path:
        warn('index.html not found. Patch it manually:')
        info(f'  CONTRACT_ADDRESS = "{contract_address}"')
        info(f'  ABI = {json.dumps(abi, indent=2)[:200]}...')
        return

    html = html_path.read_text(encoding='utf-8')

    # Inject contract address and ABI into a <script> block at the top of the app script
    web3_snippet = f"""
/* ── AUTO-DEPLOYED CONTRACT (generated by setup_deploy.py) ── */
const DEPLOYED_CONTRACT_ADDRESS = "{contract_address}";
const DEPLOYED_CONTRACT_ABI     = {json.dumps(abi, separators=(',', ':'))};
/* ─────────────────────────────────────────────────────────── */
"""

    # Insert after the opening of the babel script tag
    marker = "const { useState, useEffect"
    if marker in html:
        html = html.replace(marker, web3_snippet + marker, 1)
        # Also update the placeholder contract address in the block explorer
        html = html.replace(
            '0xa8f9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7',
            contract_address
        )
        html_path.write_text(html, encoding='utf-8')
        ok(f'Patched {html_path} with contract address {contract_address}')
    else:
        warn('Could not auto-patch HTML. Manually add:')
        info(f'  CONTRACT_ADDRESS = "{contract_address}"')


# ──────────────────────────────────────────────────────────────────────────────
INLINE_CONTRACT = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract KYCVerification {
    enum KYCStatus { NONE, SUBMITTED, APPROVED, REJECTED, REVOKED }
    struct KYCRecord {
        address userAddress; bytes32 documentHash; string ipfsCID;
        string maskedAadhaar; string panNumber; string fullName;
        KYCStatus status; uint256 submittedAt; uint256 updatedAt;
        address verifiedBy; string verifierNote;
    }
    address public owner; uint256 public totalSubmissions; uint256 public totalApproved; uint256 public totalRejected;
    mapping(address=>KYCRecord) private kycRecords;
    mapping(address=>bool) public isVerifier;
    address[] private kycUserList;

    event KYCSubmitted(address indexed user, bytes32 indexed documentHash, string ipfsCID, uint256 timestamp);
    event KYCApproved(address indexed user, address indexed verifier, string note, uint256 timestamp);
    event KYCRejected(address indexed user, address indexed verifier, string reason, uint256 timestamp);
    event KYCRevoked(address indexed user, address indexed revokedBy, string reason, uint256 timestamp);
    event VerifierAdded(address indexed verifier, address indexed addedBy, uint256 timestamp);
    event VerifierRemoved(address indexed verifier, address indexed removedBy, uint256 timestamp);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner, uint256 timestamp);

    modifier onlyOwner() { require(msg.sender==owner,"KYC: caller is not the owner"); _; }
    modifier onlyVerifier() { require(isVerifier[msg.sender],"KYC: caller is not a whitelisted verifier"); _; }
    modifier onlyOwnerOrVerifier() { require(msg.sender==owner||isVerifier[msg.sender],"KYC: caller is not owner or verifier"); _; }
    modifier kycExists(address user) { require(kycRecords[user].status!=KYCStatus.NONE,"KYC: no record found for this address"); _; }
    modifier kycNotExists(address user) { require(kycRecords[user].status==KYCStatus.NONE||kycRecords[user].status==KYCStatus.REJECTED,"KYC: record already active for this address"); _; }

    constructor() { owner=msg.sender; isVerifier[msg.sender]=true; emit VerifierAdded(msg.sender,msg.sender,block.timestamp); }

    function addVerifier(address verifier) external onlyOwner { require(verifier!=address(0),"KYC: zero address"); require(!isVerifier[verifier],"KYC: already a verifier"); isVerifier[verifier]=true; emit VerifierAdded(verifier,msg.sender,block.timestamp); }
    function removeVerifier(address verifier) external onlyOwner { require(verifier!=owner,"KYC: cannot remove owner"); require(isVerifier[verifier],"KYC: not a verifier"); isVerifier[verifier]=false; emit VerifierRemoved(verifier,msg.sender,block.timestamp); }

    function submitKYC(bytes32 documentHash, string calldata ipfsCID, string calldata maskedAadhaar, string calldata panNumber, string calldata fullName) external kycNotExists(msg.sender) {
        require(documentHash!=bytes32(0),"KYC: hash cannot be zero"); require(bytes(ipfsCID).length>0,"KYC: CID empty"); require(bytes(maskedAadhaar).length>0,"KYC: aadhaar empty"); require(bytes(panNumber).length==10,"KYC: PAN must be 10 chars"); require(bytes(fullName).length>0,"KYC: name empty");
        bool isNew=kycRecords[msg.sender].submittedAt==0;
        kycRecords[msg.sender]=KYCRecord(msg.sender,documentHash,ipfsCID,maskedAadhaar,panNumber,fullName,KYCStatus.SUBMITTED,block.timestamp,block.timestamp,address(0),"");
        if(isNew) kycUserList.push(msg.sender);
        totalSubmissions++; emit KYCSubmitted(msg.sender,documentHash,ipfsCID,block.timestamp);
    }

    function approveKYC(address user, string calldata note) external onlyVerifier kycExists(user) {
        require(kycRecords[user].status==KYCStatus.SUBMITTED,"KYC: can only approve SUBMITTED");
        kycRecords[user].status=KYCStatus.APPROVED; kycRecords[user].verifiedBy=msg.sender; kycRecords[user].verifierNote=note; kycRecords[user].updatedAt=block.timestamp;
        totalApproved++; emit KYCApproved(user,msg.sender,note,block.timestamp);
    }

    function rejectKYC(address user, string calldata reason) external onlyVerifier kycExists(user) {
        require(kycRecords[user].status==KYCStatus.SUBMITTED,"KYC: can only reject SUBMITTED"); require(bytes(reason).length>0,"KYC: rejection reason cannot be empty");
        kycRecords[user].status=KYCStatus.REJECTED; kycRecords[user].verifiedBy=msg.sender; kycRecords[user].verifierNote=reason; kycRecords[user].updatedAt=block.timestamp;
        totalRejected++; emit KYCRejected(user,msg.sender,reason,block.timestamp);
    }

    function revokeKYC(address user, string calldata reason) external onlyOwner kycExists(user) {
        require(kycRecords[user].status==KYCStatus.APPROVED,"KYC: can only revoke APPROVED"); require(bytes(reason).length>0,"KYC: reason empty");
        kycRecords[user].status=KYCStatus.REVOKED; kycRecords[user].verifierNote=reason; kycRecords[user].updatedAt=block.timestamp;
        if(totalApproved>0) totalApproved--; emit KYCRevoked(user,msg.sender,reason,block.timestamp);
    }

    function getKYCStatus(address user) external view returns (KYCStatus) { return kycRecords[user].status; }
    function isKYCVerified(address user) external view returns (bool) { return kycRecords[user].status==KYCStatus.APPROVED; }
    function getKYCRecord(address user) external view onlyOwnerOrVerifier kycExists(user) returns (KYCRecord memory) { return kycRecords[user]; }
    function getMyKYCRecord() external view returns (KYCRecord memory) { require(kycRecords[msg.sender].status!=KYCStatus.NONE,"KYC: no record"); return kycRecords[msg.sender]; }
    function getDocumentHash(address user) external view onlyOwnerOrVerifier kycExists(user) returns (bytes32) { return kycRecords[user].documentHash; }
    function verifyDocumentIntegrity(address user, bytes32 claimedHash) external view kycExists(user) returns (bool) { return kycRecords[user].documentHash==claimedHash; }
    function getTotalUsers() external view returns (uint256) { return kycUserList.length; }
    function getStats() external view returns (uint256,uint256,uint256) { return (totalSubmissions,totalApproved,totalRejected); }
    function transferOwnership(address newOwner) external onlyOwner { require(newOwner!=address(0),"KYC: zero address"); address prev=owner; owner=newOwner; isVerifier[newOwner]=true; emit OwnershipTransferred(prev,newOwner,block.timestamp); }
}
'''

# ──────────────────────────────────────────────────────────────────────────────
def print_banner():
    hr()
    print(c("""
    ⬡  ChainKYC — Automated Deployment Script
       Miqdaad Sayyed | Arfat Shaikh | Faazil Mirza Shaikh
       6th Sem BT Mini Project · Mumbai University · 2025-26
    """, 'cyan'))
    hr()

def print_summary():
    hr()
    print(c('\n  ✅  DONE! Here\'s what to do next:\n', 'green'))
    print('  1. Open chainkyc-hardhat/deployments/sepolia.json')
    print('     → Note your contract address')
    print()
    print('  2. Your index.html has been auto-patched with:')
    print('     → DEPLOYED_CONTRACT_ADDRESS')
    print('     → DEPLOYED_CONTRACT_ABI')
    print()
    print('  3. In your frontend, use ethers.js to connect:')
    print(c('     const contract = new ethers.Contract(DEPLOYED_CONTRACT_ADDRESS, DEPLOYED_CONTRACT_ABI, signer);', 'blue'))
    print()
    print('  4. View your contract on Etherscan:')
    print(c('     https://sepolia.etherscan.io/address/<your-address>', 'blue'))
    print()
    hr()

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ChainKYC Hardhat Setup & Deploy')
    parser.add_argument('--setup',   action='store_true', help='Setup project only')
    parser.add_argument('--compile', action='store_true', help='Compile contract only')
    parser.add_argument('--deploy',  action='store_true', help='Deploy to Sepolia')
    parser.add_argument('--test',    action='store_true', help='Run tests')
    args = parser.parse_args()

    print_banner()

    full_run = not any([args.setup, args.compile, args.deploy, args.test])

    try:
        check_node()

        if full_run or args.setup:
            setup_project()
            install_deps()

        if full_run or args.compile:
            compile_contract()

        if full_run or args.test:
            run_tests()

        if full_run or args.deploy:
            setup_env()
            deploy()
            print_summary()
        elif args.setup:
            ok('Setup complete! Run again with --deploy when ready.')

    except KeyboardInterrupt:
        print(c('\n\n  Interrupted by user.', 'yellow'))
        sys.exit(0)
    except RuntimeError as e:
        err(str(e))
        sys.exit(1)
