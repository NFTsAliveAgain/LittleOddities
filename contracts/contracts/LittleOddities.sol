// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC2981} from "@openzeppelin/contracts/token/common/ERC2981.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Ownable2Step} from "@openzeppelin/contracts/access/Ownable2Step.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {MerkleProof} from "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

/// @title Little Oddities — NFTs Alive Again
/// @notice 10,000 ERC-721 collectibles with a fair, provable delayed reveal.
///
/// Reveal design (prevents rarity sniping):
///  1. Before minting, the owner publishes `provenanceHash` = SHA-256 fingerprint of all
///     10,000 images in their planned order. It locks as soon as the first token is minted.
///  2. While unrevealed, every token points to the same "mystery" metadata.
///  3. `commitReveal()` (owner) picks a FUTURE block; `finalizeReveal()` (anyone) then derives
///     `startingIndex` from that block's hash. Nobody can know it in advance.
///     Token N shows planned character ((N - 1 + startingIndex) % 10000) + 1.
///  4. `reveal(baseURI)` (owner) points tokens at the final metadata. Anyone can check that
///     the final art matches the provenance hash and the on-chain startingIndex.
///
/// Every owner power is listed in docs/SMART_CONTRACT_GUIDE.md. There are no
/// hidden roles. The owner can NOT mint beyond the 500 reserve (total, ever), can
/// NOT exceed 10,000 tokens, and can NOT change metadata once it is frozen.
contract LittleOddities is ERC721, ERC2981, Ownable2Step, ReentrancyGuard {
    using Strings for uint256;

    // ---------------------------------------------------------------- limits
    uint256 public constant MAX_SUPPLY = 10_000;
    uint256 public constant RESERVED_SUPPLY = 500;
    uint256 public constant MAX_PER_TX = 4;
    uint96 public constant MAX_ROYALTY_BPS = 1_000; // 10%

    // ----------------------------------------------------------------- state
    uint256 public mintPrice = 0.005 ether;
    uint256 public walletLimit; // lifetime paid mints per wallet (allowlist + public)
    uint256 public totalSupply;
    bool public reserveMinted; // true once all 500 reserved tokens have been minted
    uint256 public reserveMintedCount; // reserved tokens minted so far (0..500)
    bool public allowlistActive;
    bool public publicActive;
    bool public metadataFrozen;
    bytes32 public merkleRoot;

    mapping(address => uint256) public mintedBy; // lifetime paid mints (allowlist + public)
    mapping(address => uint256) public allowlistMintedBy;

    string private _baseTokenURI;
    string private _unrevealedURI;
    string public provenanceHash;
    uint256 public startingIndexBlock;
    uint256 public startingIndex;
    bool public startingIndexSet;
    bool public revealed;
    string private _contractURI;

    // ---------------------------------------------------------------- events
    event MintPriceUpdated(uint256 oldPrice, uint256 newPrice);
    event WalletLimitUpdated(uint256 oldLimit, uint256 newLimit);
    event AllowlistActiveSet(bool active);
    event PublicActiveSet(bool active);
    event MerkleRootUpdated(bytes32 root);
    event ReserveMinted(address indexed to, uint256 firstTokenId, uint256 lastTokenId);
    event Minted(address indexed to, uint256 firstTokenId, uint256 quantity, bool allowlist, uint256 paid);
    event BaseURIUpdated(string uri);
    event UnrevealedURIUpdated(string uri);
    event ProvenanceHashSet(string provenanceHash);
    event RevealCommitted(uint256 startingIndexBlock);
    event StartingIndexSet(uint256 startingIndex);
    event Revealed(string baseURI);
    event ContractURIUpdated(string uri);
    event MetadataFrozen();
    event RoyaltyUpdated(address receiver, uint96 bps);
    event Withdrawn(address indexed to, uint256 amount);

    // ---------------------------------------------------------------- errors
    error SaleNotActive();
    error InvalidQuantity();
    error WrongPayment(uint256 expected, uint256 sent);
    error ExceedsSupply();
    error ExceedsWalletLimit();
    error ExceedsAllowlistAllocation();
    error InvalidProof();
    error ReserveAlreadyMinted();
    error ExceedsReserve();
    error MetadataIsFrozen();
    error ProvenanceLocked();
    error ProvenanceMissing();
    error RevealAlreadyCommitted();
    error RevealNotCommitted();
    error RevealBlockNotReached();
    error RevealCommitExpired();
    error StartingIndexAlreadySet();
    error StartingIndexNotSet();
    error AlreadyRevealed();
    error NotRevealed();
    error RoyaltyTooHigh();
    error NothingToWithdraw();
    error WithdrawFailed();
    error RenounceDisabled();

    constructor(
        address initialOwner,
        string memory unrevealedURI_,
        string memory contractURI_,
        uint256 walletLimit_,
        uint96 royaltyBps_
    ) ERC721("Little Oddities", "ODDITY") Ownable(initialOwner) {
        if (royaltyBps_ > MAX_ROYALTY_BPS) revert RoyaltyTooHigh();
        _unrevealedURI = unrevealedURI_;
        _contractURI = contractURI_;
        walletLimit = walletLimit_;
        _setDefaultRoyalty(initialOwner, royaltyBps_);
    }

    // ================================================================ minting

    /// @notice Allowlist mint. `allocation` is this wallet's maximum allowlist mints,
    ///         proven by `proof` against the published Merkle root.
    function allowlistMint(uint256 quantity, uint256 allocation, bytes32[] calldata proof)
        external
        payable
        nonReentrant
    {
        if (!allowlistActive) revert SaleNotActive();
        bytes32 leaf = keccak256(bytes.concat(keccak256(abi.encode(msg.sender, allocation))));
        if (!MerkleProof.verifyCalldata(proof, merkleRoot, leaf)) revert InvalidProof();
        if (allowlistMintedBy[msg.sender] + quantity > allocation) revert ExceedsAllowlistAllocation();
        allowlistMintedBy[msg.sender] += quantity;
        _paidMint(quantity, true);
    }

    /// @notice Public mint, 1 to 4 per transaction at the exact mint price.
    function publicMint(uint256 quantity) external payable nonReentrant {
        if (!publicActive) revert SaleNotActive();
        _paidMint(quantity, false);
    }

    function _paidMint(uint256 quantity, bool allowlist) private {
        if (quantity == 0 || quantity > MAX_PER_TX) revert InvalidQuantity();
        uint256 expected = mintPrice * quantity;
        if (msg.value != expected) revert WrongPayment(expected, msg.value); // rejects under- AND over-payment
        if (mintedBy[msg.sender] + quantity > walletLimit) revert ExceedsWalletLimit();
        // Paid mints can never eat into the 500 reserved tokens.
        if (totalSupply + quantity > _paidCap()) revert ExceedsSupply();
        mintedBy[msg.sender] += quantity;
        uint256 first = totalSupply + 1;
        totalSupply += quantity;
        for (uint256 i = 0; i < quantity; i++) {
            _safeMint(msg.sender, first + i);
        }
        emit Minted(msg.sender, first, quantity, allowlist, msg.value);
    }

    /// @notice Mint reserved community giveaway NFTs to the owner wallet, in one or more batches.
    ///         Exactly 500 in total, ever — part of the 10,000 supply, never in addition to it.
    ///         Batching exists because minting 500 in a single transaction can exceed
    ///         Ethereum's per-transaction gas limit.
    function mintReserve(uint256 quantity) external onlyOwner nonReentrant {
        if (reserveMinted) revert ReserveAlreadyMinted();
        if (quantity == 0) revert InvalidQuantity();
        if (reserveMintedCount + quantity > RESERVED_SUPPLY) revert ExceedsReserve();
        if (totalSupply + quantity > MAX_SUPPLY) revert ExceedsSupply(); // unreachable by design, kept as a guard
        reserveMintedCount += quantity;
        if (reserveMintedCount == RESERVED_SUPPLY) reserveMinted = true;
        address to = owner();
        uint256 first = totalSupply + 1;
        totalSupply += quantity;
        for (uint256 i = 0; i < quantity; i++) {
            _mint(to, first + i);
        }
        emit ReserveMinted(to, first, first + quantity - 1);
    }

    /// @dev Paid mints may never use reserved slots that haven't been minted yet.
    function _paidCap() private view returns (uint256) {
        return MAX_SUPPLY - (RESERVED_SUPPLY - reserveMintedCount);
    }

    // ============================================================ owner admin

    function setMintPrice(uint256 newPrice) external onlyOwner {
        emit MintPriceUpdated(mintPrice, newPrice);
        mintPrice = newPrice;
    }

    function setWalletLimit(uint256 newLimit) external onlyOwner {
        emit WalletLimitUpdated(walletLimit, newLimit);
        walletLimit = newLimit;
    }

    function setMerkleRoot(bytes32 root) external onlyOwner {
        merkleRoot = root;
        emit MerkleRootUpdated(root);
    }

    function setAllowlistActive(bool active) external onlyOwner {
        allowlistActive = active;
        emit AllowlistActiveSet(active);
    }

    function setPublicActive(bool active) external onlyOwner {
        publicActive = active;
        emit PublicActiveSet(active);
    }

    // ================================================================ reveal

    /// @notice Publish the provenance fingerprint. Only possible before the first token is minted.
    function setProvenanceHash(string calldata hash_) external onlyOwner {
        if (totalSupply > 0) revert ProvenanceLocked();
        provenanceHash = hash_;
        emit ProvenanceHashSet(hash_);
    }

    function setUnrevealedURI(string calldata uri) external onlyOwner {
        if (revealed) revert AlreadyRevealed();
        _unrevealedURI = uri;
        emit UnrevealedURIUpdated(uri);
    }

    /// @notice Step 1 of the reveal: choose the next block as the randomness source.
    ///         If finalizeReveal is not called within 256 blocks, the owner may commit again.
    function commitReveal() external onlyOwner {
        if (bytes(provenanceHash).length == 0) revert ProvenanceMissing();
        if (startingIndexSet) revert StartingIndexAlreadySet();
        if (startingIndexBlock != 0 && block.number <= startingIndexBlock + 256) revert RevealAlreadyCommitted();
        startingIndexBlock = block.number + 1;
        emit RevealCommitted(startingIndexBlock);
    }

    /// @notice Step 2 of the reveal: anyone can call this once the committed block exists.
    function finalizeReveal() external {
        if (startingIndexSet) revert StartingIndexAlreadySet();
        if (startingIndexBlock == 0) revert RevealNotCommitted();
        if (block.number <= startingIndexBlock) revert RevealBlockNotReached();
        bytes32 h = blockhash(startingIndexBlock);
        if (h == bytes32(0)) revert RevealCommitExpired(); // older than 256 blocks: owner commits again
        uint256 idx = uint256(keccak256(abi.encodePacked(h, block.prevrandao, address(this)))) % MAX_SUPPLY;
        if (idx == 0) idx = 1; // always shift, so token N never simply equals planned character N
        startingIndex = idx;
        startingIndexSet = true;
        emit StartingIndexSet(idx);
    }

    /// @notice Step 3: point every token at its final metadata (generated using startingIndex).
    function reveal(string calldata baseURI_) external onlyOwner {
        if (!startingIndexSet) revert StartingIndexNotSet();
        if (revealed) revert AlreadyRevealed();
        revealed = true;
        _baseTokenURI = baseURI_;
        emit Revealed(baseURI_);
    }

    /// @notice Planned character number shown by a token after reveal.
    function characterOf(uint256 tokenId) external view returns (uint256) {
        _requireOwned(tokenId);
        if (!startingIndexSet) revert StartingIndexNotSet();
        return ((tokenId - 1 + startingIndex) % MAX_SUPPLY) + 1;
    }

    /// @notice Fix the final metadata location after reveal (until frozen).
    function setBaseURI(string calldata uri) external onlyOwner {
        if (!revealed) revert NotRevealed();
        if (metadataFrozen) revert MetadataIsFrozen();
        _baseTokenURI = uri;
        emit BaseURIUpdated(uri);
    }

    function setContractURI(string calldata uri) external onlyOwner {
        _contractURI = uri;
        emit ContractURIUpdated(uri);
    }

    /// @notice Permanently locks token metadata. Cannot be undone.
    function freezeMetadata() external onlyOwner {
        if (!revealed) revert NotRevealed();
        metadataFrozen = true;
        emit MetadataFrozen();
    }

    function setRoyalty(address receiver, uint96 bps) external onlyOwner {
        if (bps > MAX_ROYALTY_BPS) revert RoyaltyTooHigh();
        _setDefaultRoyalty(receiver, bps);
        emit RoyaltyUpdated(receiver, bps);
    }

    /// @notice Sends all mint proceeds to the current owner wallet.
    function withdraw() external onlyOwner nonReentrant {
        uint256 amount = address(this).balance;
        if (amount == 0) revert NothingToWithdraw();
        (bool ok,) = payable(owner()).call{value: amount}("");
        if (!ok) revert WithdrawFailed();
        emit Withdrawn(owner(), amount);
    }

    /// @dev Renouncing would permanently strand funds and settings, so it is disabled.
    ///      Ownership can still be moved safely with transferOwnership + acceptOwnership.
    function renounceOwnership() public view override onlyOwner {
        revert RenounceDisabled();
    }

    // ================================================================== views

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        _requireOwned(tokenId);
        if (!revealed) return _unrevealedURI;
        return string.concat(_baseTokenURI, tokenId.toString(), ".json");
    }

    function contractURI() external view returns (string memory) {
        return _contractURI;
    }

    function remainingPaidSupply() external view returns (uint256) {
        return _paidCap() - totalSupply;
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC2981) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
