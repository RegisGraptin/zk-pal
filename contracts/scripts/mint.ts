const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const contract = await hre.ethers.getContractAt("ERC20Mock", "0xc3Dd1C9DE3fDb23b94ADd25185CD4df9CB4b327a");
  const tx = await contract.mint("0xbc05A23d27687d47CBc6e2AC0663E48Ae503Cf96", "1000000000");
  await tx.wait();
  console.log("Minted tokens");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});