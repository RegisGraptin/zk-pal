# Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a Hardhat Ignition module that deploys that contract.

Try running some of the following tasks:

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat ignition deploy ./ignition/modules/ERC20Mock.ts --network sapphire-testnet
npx hardhat ignition deploy ./ignition/modules/Escrow.ts --network sapphire-testnet

npx hardhat run scripts/mint.ts --network sapphire-testnet
```
