# zk-pal

Accessing cryptocurrency is becoming increasingly difficult. Users must go through centralized exchanges, complete KYC procedures, and wait for validation. This undermines the peer-to-peer spirit of blockchain.

We wanted to propose an alternative and going back to the root spirit of blockchain by leveraging existing payment method such as Paypal to buy crypto. 
Though this project, we wanted to introduce an on-ramps/off-ramps mechanism allowing people to create USDC offers in exchange of paypal transfer.

A user will create an offer on a smart contract on Oasis Sapphire, allowing them to store sensitive information as paypal handle and locking some USDC in the smart contract. Another user, willing to do a Paypal transfer, is going to "subscribe" to the smart contract. Once register, he will have to send on paypal the expected amount and download the mail from paypal for this transfer. 

Our main objective after this was to create a ZK proof with the mail, allowing us to verify the provider signature and the associated information sent. By using it and sending it to the smart contract, the smart contract can verify the information and validate it by unlocking the fund to the user.

However, when developing this solution, we came across some issue by using ZK-email. The mail provided by Paypal is reaching the maximum size limit for the noir circuit, preventing us to create a ZK proof. To handle this case, we decided to switch our approach and rely on ROFL system form Oasis. Practically, we are using a dedicated docker container in a TEE that is going to be in charge of fetching email sent on a specific address. His role will be to process all the mail address sent to this, by verifying the mail validity and extracting the user amount and handle. Then, he will be in charge of calling the Sapphire smart contract to unlock the funds.


## Worflow illustration

![User Workflow](./workflow.png)



-----------


Getting access to crypto is becoming more and more difficult. You need to pass by centralized exchange, put a KYC, wait for validation...
We are losing the peer-to-peer spirit of blockchain.

While the development of solution, we can think on how we can use day to day protocol to pay some crypto.

We wanted to propose an alternative from traditional exchange and let the possibility of the user to directly pay someone using paypal in exchange of crypto.
Democratize crypto access becoming easier.

ZK-Paypal

1. User create a escrow entry on the smart contract by locking the number of funds he wants to received on Paypal.
2. Someone register to the entry to be willing to send paypal funds
3. He sent the fund to the handle set by the user
4. He will received an email where it can generate a ZK proof associated to it with the tx number
5. He sent to the smart contract the ZK proof at the associated vote
6. On the smart contract we check the zk proof and we can check with ROFL using Paypal API the tx
7. unlock and send the fund to the user

## Oasis feedback

`sapphireHttpTransport from "@oasisprotocol/sapphire-wagmi-v2";` is not available.
Doc from https://docs.oasis.io/build/sapphire/develop/browser/
is not updated

Need to use the one defined here:
https://github.com/oasisprotocol/sapphire-paratime/tree/main/examples/wagmi-v2
