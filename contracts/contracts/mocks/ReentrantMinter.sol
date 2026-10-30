// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

interface IOddities {
    function publicMint(uint256 quantity) external payable;
}

/// @dev TEST ONLY. Tries to re-enter publicMint while receiving an NFT.
contract ReentrantMinter {
    IOddities public target;
    bool public attempted;

    constructor(address t) { target = IOddities(t); }

    function attack() external payable {
        target.publicMint{value: msg.value}(1);
    }

    function onERC721Received(address, address, uint256, bytes calldata) external returns (bytes4) {
        if (!attempted) {
            attempted = true;
            target.publicMint{value: 0}(1); // must revert (reentrancy guard)
        }
        return this.onERC721Received.selector;
    }

    receive() external payable {}
}
