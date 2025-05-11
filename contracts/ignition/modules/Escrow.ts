// This setup uses Hardhat Ignition to manage smart contract deployments.
// Learn more about it at https://hardhat.org/ignition

import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const EscrowModule = buildModule("EscrowModule", (m) => {
  const escrow = m.contract("Escrow", [
    "0xc3Dd1C9DE3fDb23b94ADd25185CD4df9CB4b327a", 
    "rofl1qrcc2y5lvhx45dd8dgzlwa3luxxwkwalautdg8hv",
    "0xc3Dd1C9DE3fDb23b94ADd25185CD4df9CB4b327a"
  ], {});
  return { escrow };
});

export default EscrowModule;
