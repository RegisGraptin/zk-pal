// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Escrow {
    
    enum Status {
        AVAILABLE,
        ONGOING,
        FINISHED
    }

    // https://docs.oasis.io/build/sapphire/addresses
    address constant USDC = 0x97eec1c29f745dC7c267F90292AA663d997a601D; 

    struct EscrowEntry {
        address creator;
        string paypalHandle;
        uint256 amount;
        Status status;
    }

    /// @notice Track the last ID 
    uint256 lastEntryId;

    mapping(uint256 => EscrowEntry) private entries;
    mapping(uint256 => address) private isLocked;

    uint256[] public activeEntries;


    function createEntry(
        string memory paypalHandle,
        uint256 amount
    ) external {
        IERC20(USDC).transferFrom(msg.sender, address(this), amount);
        entries[lastEntryId] = EscrowEntry({
            creator: msg.sender,
            paypalHandle: paypalHandle,
            amount: amount,
            status: Status.AVAILABLE
        });
        activeEntries.push(lastEntryId);
        lastEntryId++;
    }


    /// @notice Lock the entry for future paypal paiment
    function subscribe(uint256 id) external {
        require(isLocked[id] == address(0), "NEED_TO_BE_LOCK");
        isLocked[id] = msg.sender;
        entries[id].status = Status.ONGOING;
    }

    function proofOfPaiement(uint256 id) external {

    }

}