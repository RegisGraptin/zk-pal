// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import { SiweAuth } from "@oasisprotocol/sapphire-contracts/contracts/auth/SiweAuth.sol";
import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "./ERC20Mock.sol";

contract Escrow is SiweAuth {
    
    enum Status {
        AVAILABLE,
        ONGOING,
        FINISHED
    }

    // https://docs.oasis.io/build/sapphire/addresses
    // address constant USDC = 0x97eec1c29f745dC7c267F90292AA663d997a601D; 
    address public USDC;

    struct EscrowEntry {
        address creator;
        string paypalHandle;
        uint256 amount;
        Status status;
    }

    error InsufficientFund();

    event NewSubscription(uint256, address);

    /// @notice Track the last ID 
    uint256 lastEntryId;

    mapping(uint256 => EscrowEntry) private entries;
    mapping(string => uint256) private handleToId;
    mapping(uint256 => address) public isLocked;

    uint256[] public activeEntries;

    constructor (address _usdc) SiweAuth("localhost") {
        USDC = _usdc;
    }

    function getActiveEntries() external view returns (uint256[] memory) {
        return activeEntries;
    }

    function getEntry(uint256 id) external view returns (uint256, Status) {
        EscrowEntry memory entry = entries[id];
        return (entry.amount, entry.status);
    }

    function getPaypalHandle(uint256 id, bytes memory token) external view returns (string memory) {
        require(isLocked[id] == msg.sender || isLocked[id] == authMsgSender(token), "NOT_AUTHORIZED");
        return entries[id].paypalHandle;
    }
      
    function createEntry(
        string memory paypalHandle,
        uint256 amount
    ) external {
        require(handleToId[paypalHandle] == 0, "ALREADY_USED_HANDLE");
        IERC20(USDC).transferFrom(msg.sender, address(this), amount);
        entries[lastEntryId] = EscrowEntry({
            creator: msg.sender,
            paypalHandle: paypalHandle,
            amount: amount,
            status: Status.AVAILABLE
        });
        handleToId[paypalHandle] = lastEntryId;
        activeEntries.push(lastEntryId);
        lastEntryId++;
    }


    /// @notice Lock the entry for future paypal paiment
    function subscribe(uint256 id) external {
        require(isLocked[id] == address(0), "NEED_TO_BE_LOCK");
        isLocked[id] = msg.sender;
        entries[id].status = Status.ONGOING;
        emit NewSubscription(id, msg.sender);
    }

    // FIXME: add modifier only app ID
    function proofOfPaiement(string memory handle, uint256 amount) external {
        uint256 entryId = handleToId[handle];
        if (amount < entries[entryId].amount) {
            revert InsufficientFund();
        }
        require(isLocked[entryId] != address(0), "NO_SUBSCRIPTION");
        
        // Unlock the USDC
        IERC20(USDC).transfer(isLocked[entryId], entries[entryId].amount);

        // Clean the environment varialbe
        entries[entryId].status = Status.FINISHED;

        delete isLocked[entryId];
        delete handleToId[handle];

        // TODO: Should we clean the list of id?
    }

}