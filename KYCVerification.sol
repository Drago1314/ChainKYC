// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title KYCVerification
 * @author Miqdaad Sayyed, Arfat Shaikh, Faazil Mirza Shaikh
 * @notice Blockchain-based Secure KYC Verification System
 *         6th Semester Mini Project — Blockchain Technology
 *         BE Computer Engineering — Mumbai University — 2024-25
 *
 * @dev This contract manages KYC (Know Your Customer) records on the
 *      Ethereum blockchain. Document hashes are stored immutably on-chain
 *      while actual documents are stored on IPFS (off-chain).
 *
 * Architecture:
 *  - Owner deploys contract and manages the verifier whitelist
 *  - Users submit KYC by providing their document hash + IPFS CID
 *  - Whitelisted verifiers can APPROVE or REJECT submissions
 *  - All state changes emit events for full auditability
 *  - Owner can revoke previously approved KYC if required
 */
contract KYCVerification {

    /* ─────────────────────── ENUMS ─────────────────────────────── */

    /**
     * @dev KYC status state machine:
     *      NONE → SUBMITTED → APPROVED
     *                       → REJECTED
     *      APPROVED → REVOKED (owner only)
     */
    enum KYCStatus {
        NONE,       // 0: No KYC record exists
        SUBMITTED,  // 1: User submitted, awaiting review
        APPROVED,   // 2: Verifier approved
        REJECTED,   // 3: Verifier rejected
        REVOKED     // 4: Owner revoked a previously approved KYC
    }

    /* ─────────────────────── STRUCTS ───────────────────────────── */

    struct KYCRecord {
        address userAddress;      // Ethereum wallet of the user
        bytes32 documentHash;     // SHA-256 hash of document bundle
        string  ipfsCID;          // IPFS CID of encrypted document bundle
        string  maskedAadhaar;    // Last 4 digits only: "****-****-XXXX"
        string  panNumber;        // PAN card number
        string  fullName;         // Legal full name
        KYCStatus status;         // Current KYC status
        uint256 submittedAt;      // Block timestamp of submission
        uint256 updatedAt;        // Block timestamp of last status update
        address verifiedBy;       // Address of verifier who acted on this
        string  verifierNote;     // Note from verifier (reason for rejection etc.)
    }

    /* ─────────────────────── STATE VARS ───────────────────────── */

    address public owner;
    uint256 public totalSubmissions;
    uint256 public totalApproved;
    uint256 public totalRejected;

    // userAddress → KYCRecord
    mapping(address => KYCRecord) private kycRecords;

    // whitelisted verifier addresses
    mapping(address => bool) public isVerifier;

    // list of all users who have submitted KYC (for enumeration)
    address[] private kycUserList;

    /* ─────────────────────── EVENTS ───────────────────────────── */

    event KYCSubmitted(
        address indexed user,
        bytes32 indexed documentHash,
        string  ipfsCID,
        uint256 timestamp
    );

    event KYCApproved(
        address indexed user,
        address indexed verifier,
        string  note,
        uint256 timestamp
    );

    event KYCRejected(
        address indexed user,
        address indexed verifier,
        string  reason,
        uint256 timestamp
    );

    event KYCRevoked(
        address indexed user,
        address indexed revokedBy,
        string  reason,
        uint256 timestamp
    );

    event VerifierAdded(
        address indexed verifier,
        address indexed addedBy,
        uint256 timestamp
    );

    event VerifierRemoved(
        address indexed verifier,
        address indexed removedBy,
        uint256 timestamp
    );

    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner,
        uint256 timestamp
    );

    /* ─────────────────────── MODIFIERS ────────────────────────── */

    modifier onlyOwner() {
        require(msg.sender == owner, "KYC: caller is not the owner");
        _;
    }

    modifier onlyVerifier() {
        require(isVerifier[msg.sender], "KYC: caller is not a whitelisted verifier");
        _;
    }

    modifier onlyOwnerOrVerifier() {
        require(
            msg.sender == owner || isVerifier[msg.sender],
            "KYC: caller is not owner or verifier"
        );
        _;
    }

    modifier kycExists(address user) {
        require(
            kycRecords[user].status != KYCStatus.NONE,
            "KYC: no record found for this address"
        );
        _;
    }

    modifier kycNotExists(address user) {
        require(
            kycRecords[user].status == KYCStatus.NONE ||
            kycRecords[user].status == KYCStatus.REJECTED,
            "KYC: record already active for this address"
        );
        _;
    }

    /* ─────────────────────── CONSTRUCTOR ──────────────────────── */

    constructor() {
        owner = msg.sender;
        isVerifier[msg.sender] = true; // Owner is also a verifier by default
        emit VerifierAdded(msg.sender, msg.sender, block.timestamp);
    }

    /* ─────────────────────── VERIFIER MGMT ────────────────────── */

    /**
     * @notice Add a new whitelisted verifier
     * @param verifier Address to whitelist as a verifier
     */
    function addVerifier(address verifier) external onlyOwner {
        require(verifier != address(0), "KYC: zero address not allowed");
        require(!isVerifier[verifier],  "KYC: address is already a verifier");
        isVerifier[verifier] = true;
        emit VerifierAdded(verifier, msg.sender, block.timestamp);
    }

    /**
     * @notice Remove a verifier from the whitelist
     * @param verifier Address to remove from verifier whitelist
     */
    function removeVerifier(address verifier) external onlyOwner {
        require(verifier != owner,     "KYC: cannot remove owner as verifier");
        require(isVerifier[verifier],  "KYC: address is not a verifier");
        isVerifier[verifier] = false;
        emit VerifierRemoved(verifier, msg.sender, block.timestamp);
    }

    /* ─────────────────────── KYC SUBMISSION ───────────────────── */

    /**
     * @notice Submit a new KYC record
     * @dev    Only the document HASH is stored on-chain (privacy-preserving).
     *         Actual documents are encrypted and stored on IPFS.
     *
     * @param documentHash  SHA-256 hash of the encrypted document bundle
     * @param ipfsCID       IPFS Content Identifier of the encrypted document bundle
     * @param maskedAadhaar Masked Aadhaar number (last 4 digits only)
     * @param panNumber     PAN card number
     * @param fullName      Full legal name of the applicant
     */
    function submitKYC(
        bytes32 documentHash,
        string  calldata ipfsCID,
        string  calldata maskedAadhaar,
        string  calldata panNumber,
        string  calldata fullName
    ) external kycNotExists(msg.sender) {
        require(documentHash != bytes32(0),       "KYC: document hash cannot be zero");
        require(bytes(ipfsCID).length > 0,        "KYC: IPFS CID cannot be empty");
        require(bytes(maskedAadhaar).length > 0,  "KYC: Aadhaar cannot be empty");
        require(bytes(panNumber).length == 10,    "KYC: PAN must be 10 characters");
        require(bytes(fullName).length > 0,       "KYC: Full name cannot be empty");

        bool isNewUser = kycRecords[msg.sender].submittedAt == 0;

        kycRecords[msg.sender] = KYCRecord({
            userAddress:    msg.sender,
            documentHash:   documentHash,
            ipfsCID:        ipfsCID,
            maskedAadhaar:  maskedAadhaar,
            panNumber:      panNumber,
            fullName:       fullName,
            status:         KYCStatus.SUBMITTED,
            submittedAt:    block.timestamp,
            updatedAt:      block.timestamp,
            verifiedBy:     address(0),
            verifierNote:   ""
        });

        if (isNewUser) {
            kycUserList.push(msg.sender);
        }

        totalSubmissions++;

        emit KYCSubmitted(msg.sender, documentHash, ipfsCID, block.timestamp);
    }

    /* ─────────────────────── KYC VERIFICATION ─────────────────── */

    /**
     * @notice Approve a pending KYC submission
     * @param user  Address of the user whose KYC to approve
     * @param note  Optional note from the verifier
     */
    function approveKYC(address user, string calldata note)
        external
        onlyVerifier
        kycExists(user)
    {
        require(
            kycRecords[user].status == KYCStatus.SUBMITTED,
            "KYC: can only approve SUBMITTED records"
        );

        kycRecords[user].status       = KYCStatus.APPROVED;
        kycRecords[user].verifiedBy   = msg.sender;
        kycRecords[user].verifierNote = note;
        kycRecords[user].updatedAt    = block.timestamp;

        totalApproved++;

        emit KYCApproved(user, msg.sender, note, block.timestamp);
    }

    /**
     * @notice Reject a pending KYC submission
     * @param user   Address of the user whose KYC to reject
     * @param reason Reason for rejection (stored on-chain for transparency)
     */
    function rejectKYC(address user, string calldata reason)
        external
        onlyVerifier
        kycExists(user)
    {
        require(
            kycRecords[user].status == KYCStatus.SUBMITTED,
            "KYC: can only reject SUBMITTED records"
        );
        require(bytes(reason).length > 0, "KYC: rejection reason cannot be empty");

        kycRecords[user].status       = KYCStatus.REJECTED;
        kycRecords[user].verifiedBy   = msg.sender;
        kycRecords[user].verifierNote = reason;
        kycRecords[user].updatedAt    = block.timestamp;

        totalRejected++;

        emit KYCRejected(user, msg.sender, reason, block.timestamp);
    }

    /**
     * @notice Revoke a previously approved KYC (owner only)
     * @param user   Address of the user whose KYC to revoke
     * @param reason Reason for revocation
     */
    function revokeKYC(address user, string calldata reason)
        external
        onlyOwner
        kycExists(user)
    {
        require(
            kycRecords[user].status == KYCStatus.APPROVED,
            "KYC: can only revoke APPROVED records"
        );
        require(bytes(reason).length > 0, "KYC: revocation reason cannot be empty");

        kycRecords[user].status       = KYCStatus.REVOKED;
        kycRecords[user].verifierNote = reason;
        kycRecords[user].updatedAt    = block.timestamp;

        if (totalApproved > 0) totalApproved--;

        emit KYCRevoked(user, msg.sender, reason, block.timestamp);
    }

    /* ─────────────────────── VIEW FUNCTIONS ───────────────────── */

    /**
     * @notice Get the KYC status of a user (publicly callable)
     * @param user  Address to query
     * @return      KYCStatus enum value
     */
    function getKYCStatus(address user) external view returns (KYCStatus) {
        return kycRecords[user].status;
    }

    /**
     * @notice Check if a user's KYC is approved (simple boolean check)
     * @param user  Address to check
     * @return      true if KYC is APPROVED, false otherwise
     */
    function isKYCVerified(address user) external view returns (bool) {
        return kycRecords[user].status == KYCStatus.APPROVED;
    }

    /**
     * @notice Get full KYC record (caller must be owner or verifier)
     * @param user  Address whose record to fetch
     * @return      Full KYCRecord struct
     */
    function getKYCRecord(address user)
        external
        view
        onlyOwnerOrVerifier
        kycExists(user)
        returns (KYCRecord memory)
    {
        return kycRecords[user];
    }

    /**
     * @notice Get user's own KYC record (public — any user can read their own)
     * @return  KYCRecord of msg.sender
     */
    function getMyKYCRecord() external view returns (KYCRecord memory) {
        require(
            kycRecords[msg.sender].status != KYCStatus.NONE,
            "KYC: no record found for your address"
        );
        return kycRecords[msg.sender];
    }

    /**
     * @notice Get document hash of a user (owner/verifier only)
     * @param user  Address to query
     * @return      SHA-256 document hash stored on-chain
     */
    function getDocumentHash(address user)
        external
        view
        onlyOwnerOrVerifier
        kycExists(user)
        returns (bytes32)
    {
        return kycRecords[user].documentHash;
    }

    /**
     * @notice Verify document integrity by comparing provided hash against stored hash
     * @param user          Address of the user
     * @param claimedHash   Hash to verify against the stored value
     * @return              true if hashes match
     */
    function verifyDocumentIntegrity(address user, bytes32 claimedHash)
        external
        view
        kycExists(user)
        returns (bool)
    {
        return kycRecords[user].documentHash == claimedHash;
    }

    /**
     * @notice Get count of all KYC users
     * @return  Number of unique users who have submitted KYC
     */
    function getTotalUsers() external view returns (uint256) {
        return kycUserList.length;
    }

    /**
     * @notice Get paginated list of KYC users (owner/verifier only)
     * @param offset  Starting index
     * @param limit   Number of records to return
     * @return        Array of user addresses
     */
    function getKYCUsers(uint256 offset, uint256 limit)
        external
        view
        onlyOwnerOrVerifier
        returns (address[] memory)
    {
        require(offset < kycUserList.length, "KYC: offset out of bounds");
        uint256 end = offset + limit;
        if (end > kycUserList.length) end = kycUserList.length;
        address[] memory result = new address[](end - offset);
        for (uint256 i = offset; i < end; i++) {
            result[i - offset] = kycUserList[i];
        }
        return result;
    }

    /**
     * @notice Get platform-wide statistics
     * @return submissions  Total KYC submissions
     * @return approved     Total approved KYCs
     * @return rejected     Total rejected KYCs
     */
    function getStats()
        external
        view
        returns (uint256 submissions, uint256 approved, uint256 rejected)
    {
        return (totalSubmissions, totalApproved, totalRejected);
    }

    /* ─────────────────────── ADMIN ────────────────────────────── */

    /**
     * @notice Transfer contract ownership
     * @param newOwner  Address of the new owner
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "KYC: new owner is the zero address");
        address previousOwner = owner;
        owner = newOwner;
        isVerifier[newOwner] = true;
        emit OwnershipTransferred(previousOwner, newOwner, block.timestamp);
    }
}
