# zk-pal

ZK-Paypal 


1. User create a escrow entry on the smart contract by locking the number of funds he wants to received on Paypal.
2. Someone register to the entry to be willing to send paypal funds
3. He sent the fund to the handle set by the user 
4. He will received an email where it can generate a ZK proof associated to it with the tx number
5. He sent to the smart contract the ZK proof at the associated vote
6. On the smart contract we check the zk proof and we can check with ROFL using Paypal API the tx
7. unlock and send the fund to the user


