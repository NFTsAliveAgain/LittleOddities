const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");
const { StandardMerkleTree } = require("@openzeppelin/merkle-tree");

const PRICE = ethers.parseEther("0.005");
const BASE = "ipfs://bafyTESTONLY/";

describe("LittleOddities", function () {
  async function deploy() {
    const [owner, alice, bob, carol, mallory] = await ethers.getSigners();
    const F = await ethers.getContractFactory("LittleOddities");
    const c = await F.deploy(owner.address, BASE, "ipfs://bafyTESTONLY/collection.json", 10, 500);
    const tree = StandardMerkleTree.of([[alice.address, "3"], [bob.address, "8"]], ["address", "uint256"]);
    return { c, owner, alice, bob, carol, mallory, tree };
  }
  async function deployLive() {
    const f = await deploy();
    await f.c.setPublicActive(true);
    return f;
  }
  const proofFor = (tree, addr) => {
    for (const [i, v] of tree.entries()) if (v[0] === addr) return { proof: tree.getProof(i), alloc: v[1] };
  };

  describe("defaults", function () {
    it("has correct constants and initial settings", async function () {
      const { c, owner } = await loadFixture(deploy);
      expect(await c.MAX_SUPPLY()).to.equal(10000n);
      expect(await c.RESERVED_SUPPLY()).to.equal(500n);
      expect(await c.MAX_PER_TX()).to.equal(4n);
      expect(await c.mintPrice()).to.equal(PRICE);
      expect(await c.walletLimit()).to.equal(10n);
      expect(await c.owner()).to.equal(owner.address);
      expect(await c.name()).to.equal("Little Oddities");
    });
    it("public and allowlist minting are disabled by default", async function () {
      const { c, alice } = await loadFixture(deploy);
      expect(await c.publicActive()).to.equal(false);
      expect(await c.allowlistActive()).to.equal(false);
      await expect(c.connect(alice).publicMint(1, { value: PRICE })).to.be.revertedWithCustomError(c, "SaleNotActive");
    });
  });

  describe("public mint pricing and limits", function () {
    for (const q of [1, 2, 3, 4]) {
      it(`mints ${q} for exactly ${q} x 0.005 ETH`, async function () {
        const { c, alice } = await loadFixture(deployLive);
        await expect(c.connect(alice).publicMint(q, { value: PRICE * BigInt(q) }))
          .to.changeEtherBalance(c, PRICE * BigInt(q));
        expect(await c.balanceOf(alice.address)).to.equal(BigInt(q));
      });
    }
    it("rejects underpayment", async function () {
      const { c, alice } = await loadFixture(deployLive);
      await expect(c.connect(alice).publicMint(2, { value: PRICE })).to.be.revertedWithCustomError(c, "WrongPayment")
        .withArgs(PRICE * 2n, PRICE);
    });
    it("rejects overpayment instead of keeping it", async function () {
      const { c, alice } = await loadFixture(deployLive);
      await expect(c.connect(alice).publicMint(1, { value: PRICE + 1n })).to.be.revertedWithCustomError(c, "WrongPayment");
    });
    it("rejects 0 and more than 4 per transaction", async function () {
      const { c, alice } = await loadFixture(deployLive);
      await expect(c.connect(alice).publicMint(0, { value: 0 })).to.be.revertedWithCustomError(c, "InvalidQuantity");
      await expect(c.connect(alice).publicMint(5, { value: PRICE * 5n })).to.be.revertedWithCustomError(c, "InvalidQuantity");
    });
    it("enforces the lifetime wallet limit separately from the per-tx limit", async function () {
      const { c, alice } = await loadFixture(deployLive);
      await c.connect(alice).publicMint(4, { value: PRICE * 4n });
      await c.connect(alice).publicMint(4, { value: PRICE * 4n });
      await expect(c.connect(alice).publicMint(3, { value: PRICE * 3n })).to.be.revertedWithCustomError(c, "ExceedsWalletLimit");
      await c.connect(alice).publicMint(2, { value: PRICE * 2n }); // exactly 10
      expect(await c.mintedBy(alice.address)).to.equal(10n);
    });
    it("owner can change the wallet limit and price, with events", async function () {
      const { c, alice } = await loadFixture(deployLive);
      await expect(c.setWalletLimit(2)).to.emit(c, "WalletLimitUpdated").withArgs(10, 2);
      await expect(c.connect(alice).publicMint(3, { value: PRICE * 3n })).to.be.revertedWithCustomError(c, "ExceedsWalletLimit");
      const newPrice = ethers.parseEther("0.01");
      await expect(c.setMintPrice(newPrice)).to.emit(c, "MintPriceUpdated").withArgs(PRICE, newPrice);
      await expect(c.connect(alice).publicMint(1, { value: PRICE })).to.be.revertedWithCustomError(c, "WrongPayment");
      await c.connect(alice).publicMint(1, { value: newPrice });
    });
  });

  describe("sequential ids and metadata", function () {
    it("mints sequential ids starting at 1 with correct tokenURI", async function () {
      const { c, alice, bob } = await loadFixture(deployLive);
      await expect(c.connect(alice).publicMint(2, { value: PRICE * 2n })).to.emit(c, "Minted").withArgs(alice.address, 1, 2, false, PRICE * 2n);
      await c.connect(bob).publicMint(1, { value: PRICE });
      expect(await c.ownerOf(1)).to.equal(alice.address);
      expect(await c.ownerOf(2)).to.equal(alice.address);
      expect(await c.ownerOf(3)).to.equal(bob.address);
      expect(await c.tokenURI(3)).to.equal(BASE + "3.json");
      expect(await c.totalSupply()).to.equal(3n);
      await expect(c.tokenURI(4)).to.be.revertedWithCustomError(c, "ERC721NonexistentToken");
    });
    it("base URI can be updated until frozen, then never again", async function () {
      const { c, alice } = await loadFixture(deployLive);
      await c.connect(alice).publicMint(1, { value: PRICE });
      await expect(c.setBaseURI("ipfs://bafyNEW/")).to.emit(c, "BaseURIUpdated");
      expect(await c.tokenURI(1)).to.equal("ipfs://bafyNEW/1.json");
      await expect(c.freezeMetadata()).to.emit(c, "MetadataFrozen");
      await expect(c.setBaseURI("ipfs://other/")).to.be.revertedWithCustomError(c, "MetadataIsFrozen");
    });
    it("supports ERC-721 and ERC-2981 interfaces with a capped royalty", async function () {
      const { c, owner } = await loadFixture(deploy);
      expect(await c.supportsInterface("0x80ac58cd")).to.equal(true);
      expect(await c.supportsInterface("0x2a55205a")).to.equal(true);
      const [recv, amt] = await c.royaltyInfo(1, 10000);
      expect(recv).to.equal(owner.address);
      expect(amt).to.equal(500n);
      await expect(c.setRoyalty(owner.address, 1001)).to.be.revertedWithCustomError(c, "RoyaltyTooHigh");
    });
  });

  describe("allowlist (Merkle)", function () {
    async function withList() {
      const f = await deploy();
      await f.c.setMerkleRoot(f.tree.root);
      await f.c.setAllowlistActive(true);
      return f;
    }
    it("lets listed wallets mint up to their allocation", async function () {
      const { c, alice, tree } = await loadFixture(withList);
      const { proof, alloc } = proofFor(tree, alice.address);
      await c.connect(alice).allowlistMint(2, alloc, proof, { value: PRICE * 2n });
      await c.connect(alice).allowlistMint(1, alloc, proof, { value: PRICE });
      await expect(c.connect(alice).allowlistMint(1, alloc, proof, { value: PRICE })).to.be.revertedWithCustomError(c, "ExceedsAllowlistAllocation");
    });
    it("rejects wallets not on the list, wrong allocations and stolen proofs", async function () {
      const { c, alice, carol, tree } = await loadFixture(withList);
      const { proof, alloc } = proofFor(tree, alice.address);
      await expect(c.connect(carol).allowlistMint(1, alloc, proof, { value: PRICE })).to.be.revertedWithCustomError(c, "InvalidProof");
      await expect(c.connect(alice).allowlistMint(1, 50, proof, { value: PRICE })).to.be.revertedWithCustomError(c, "InvalidProof");
      await expect(c.connect(carol).allowlistMint(1, 1, [], { value: PRICE })).to.be.revertedWithCustomError(c, "InvalidProof");
    });
    it("still enforces price, 4-per-tx and wallet limits", async function () {
      const { c, bob, tree } = await loadFixture(withList);
      const { proof, alloc } = proofFor(tree, bob.address);
      await expect(c.connect(bob).allowlistMint(5, alloc, proof, { value: PRICE * 5n })).to.be.revertedWithCustomError(c, "InvalidQuantity");
      await expect(c.connect(bob).allowlistMint(1, alloc, proof, { value: 0 })).to.be.revertedWithCustomError(c, "WrongPayment");
      await c.setWalletLimit(5);
      await c.connect(bob).allowlistMint(4, alloc, proof, { value: PRICE * 4n });
      await expect(c.connect(bob).allowlistMint(2, alloc, proof, { value: PRICE * 2n })).to.be.revertedWithCustomError(c, "ExceedsWalletLimit");
    });
    it("is off unless activated, independently of public mint", async function () {
      const { c, alice, tree } = await loadFixture(deploy);
      await c.setMerkleRoot(tree.root);
      const { proof, alloc } = proofFor(tree, alice.address);
      await expect(c.connect(alice).allowlistMint(1, alloc, proof, { value: PRICE })).to.be.revertedWithCustomError(c, "SaleNotActive");
    });
  });

  describe("500 reserved giveaway NFTs", function () {
    it("mints exactly 500 to the owner once, free, with an event", async function () {
      const { c, owner } = await loadFixture(deploy);
      const tx = c.mintReserve();
      await expect(tx).to.emit(c, "ReserveMinted").withArgs(owner.address, 1, 500);
      expect(await c.balanceOf(owner.address)).to.equal(500n);
      expect(await c.totalSupply()).to.equal(500n);
      const r = await (await tx).wait?.();
      await expect(c.mintReserve()).to.be.revertedWithCustomError(c, "ReserveAlreadyMinted");
    });
    it("reports reserve gas usage", async function () {
      const { c } = await loadFixture(deploy);
      const rc = await (await c.mintReserve()).wait();
      console.log(`      reserve mint gas used: ${rc.gasUsed}`);
      expect(rc.gasUsed).to.be.lessThan(30_000_000n);
    });
    it("cannot be called by anyone but the owner", async function () {
      const { c, mallory } = await loadFixture(deploy);
      await expect(c.connect(mallory).mintReserve()).to.be.revertedWithCustomError(c, "OwnableUnauthorizedAccount");
    });
    it("paid mints can never use the reserved 500, and supply never exceeds 10,000", async function () {
      const { c, owner } = await loadFixture(deployLive);
      await c.setWalletLimit(100000);
      await c.setMintPrice(0); // test-only shortcut to fill supply quickly
      expect(await c.remainingPaidSupply()).to.equal(9500n);
      const signers = await ethers.getSigners();
      // fill 9,500 paid tokens using the owner wallet (4 per tx)
      for (let i = 0; i < 2375; i++) await c.publicMint(4);
      expect(await c.totalSupply()).to.equal(9500n);
      await expect(c.publicMint(1)).to.be.revertedWithCustomError(c, "ExceedsSupply");
      await c.mintReserve();
      expect(await c.totalSupply()).to.equal(10000n);
      expect(await c.ownerOf(10000)).to.equal(owner.address);
      await expect(c.publicMint(1)).to.be.revertedWithCustomError(c, "ExceedsSupply");
      expect(await c.remainingPaidSupply()).to.equal(0n);
    });
  });

  describe("owner-only functions and ownership", function () {
    it("blocks every admin function for non-owners", async function () {
      const { c, mallory } = await loadFixture(deploy);
      const m = c.connect(mallory);
      for (const call of [
        () => m.setMintPrice(1), () => m.setWalletLimit(1), () => m.setMerkleRoot(ethers.ZeroHash),
        () => m.setAllowlistActive(true), () => m.setPublicActive(true), () => m.setBaseURI("x"),
        () => m.setContractURI("x"), () => m.freezeMetadata(), () => m.setRoyalty(mallory.address, 1),
        () => m.withdraw(), () => m.mintReserve(), () => m.transferOwnership(mallory.address),
      ]) {
        await expect(call()).to.be.revertedWithCustomError(c, "OwnableUnauthorizedAccount");
      }
    });
    it("withdraws all proceeds to the owner only", async function () {
      const { c, owner, alice, mallory } = await loadFixture(deployLive);
      await c.connect(alice).publicMint(4, { value: PRICE * 4n });
      await expect(c.connect(mallory).withdraw()).to.be.revertedWithCustomError(c, "OwnableUnauthorizedAccount");
      await expect(c.withdraw()).to.changeEtherBalances([c, owner], [-(PRICE * 4n), PRICE * 4n]);
      await expect(c.withdraw()).to.be.revertedWithCustomError(c, "NothingToWithdraw");
    });
    it("transfers ownership in two steps; reserve then goes to the new owner", async function () {
      const { c, owner, carol } = await loadFixture(deploy);
      await c.transferOwnership(carol.address);
      expect(await c.owner()).to.equal(owner.address); // not yet accepted
      await c.connect(carol).acceptOwnership();
      expect(await c.owner()).to.equal(carol.address);
      await expect(c.setMintPrice(1)).to.be.revertedWithCustomError(c, "OwnableUnauthorizedAccount");
      await c.connect(carol).mintReserve();
      expect(await c.balanceOf(carol.address)).to.equal(500n);
    });
    it("blocks reentrancy through onERC721Received", async function () {
      const { c } = await loadFixture(deployLive);
      const A = await (await ethers.getContractFactory("ReentrantMinter")).deploy(await c.getAddress());
      await expect(A.attack({ value: PRICE })).to.be.revertedWithCustomError(c, "ReentrancyGuardReentrantCall");
      expect(await c.totalSupply()).to.equal(0n);
    });
    it("cannot renounce ownership by accident", async function () {
      const { c } = await loadFixture(deploy);
      await expect(c.renounceOwnership()).to.be.revertedWithCustomError(c, "RenounceDisabled");
    });
  });
});
