// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {Escrow} from "../contracts/Escrow.sol";
import {ERC20Mock} from "../contracts/ERC20Mock.sol";



contract EscrowTest is Test {
    Escrow public escrow;
    ERC20Mock public erc20;

    function setUp() public {
        erc20 = new ERC20Mock();
        escrow = new Escrow(address(erc20));
    }

    function test_CreateEntry() public {
        erc20.mint(address(this), 10);
        erc20.approve(address(escrow), 10);
        escrow.createEntry(
            "test",
            10
        );

        (uint256 amount, Escrow.Status status) = escrow.getEntry(0);
        assert(amount == 10);
        assert(status == Escrow.Status.AVAILABLE);
    }

}
