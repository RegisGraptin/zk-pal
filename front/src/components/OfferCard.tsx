import { SiweMessage } from "siwe";
import { formatUnits, getAddress, toHex } from "viem";
import SubmitEmailModal from "./SubmitEmailModal";
import { useAccount, useReadContract, useWriteContract } from "wagmi";

import Escrow from "@/data/Escrow.json";
import { ethers } from "ethers";
import { useEffect, useState } from "react";

enum Status {
  AVAILABLE = 0,
  ONGOING = 1,
  FINISHED = 2,
}

interface OfferCardProps {
  offerId: number;
  offer: [bigint, number];
}

export default function OfferCard({ offerId, offer }: OfferCardProps) {
  const { address: userAddress } = useAccount();

  const [signature, setSignature] = useState();
  const [siweMsg, setSiweMsg] = useState();

  const { writeContract } = useWriteContract();

  const subscribeToTheOffer = () => {
    console.log("subscribeToTheOffer");
    writeContract({
      address: getAddress(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS!),
      abi: Escrow.abi,
      functionName: "subscribe",
      args: [offerId],
    });
  };

  const { data: lockedAddress } = useReadContract({
    address: getAddress(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS!),
    abi: Escrow.abi,
    functionName: "isLocked",
    args: [offerId],
  });

  // token = await messageBox.(siweMsg, sig);

  const { data: token, error } = useReadContract({
    address: getAddress(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS!),
    abi: Escrow.abi,
    functionName: "login",
    args: [siweMsg, signature],
    query: {
      enabled: !!signature && !!siweMsg,
    },
  });

  console.log(siweMsg);
  console.log("signature", signature);

  console.log("error", error);
  console.log("token", token);

  // const {
  //   data: paypalHandle,
  //   error,
  //   isPending,
  // } = useReadContract({
  //   address: getAddress(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS!),
  //   abi: Escrow.abi,
  //   functionName: "getPaypalHandle",
  //   args: [offerId, signature],
  //   query: {
  //     enabled: !!signature,
  //   },
  // });

  // console.log(paypalHandle);
  // console.log(error);

  useEffect(() => {
    if (signature) return;
    if (userAddress == lockedAddress) {
      getSecretMessage();
    }
  }, [userAddress, lockedAddress]);

  async function getSecretMessage() {
    // Stored in browser session.
    const siweMsg = new SiweMessage({
      domain: "localhost",
      address: userAddress, // User's selected account address.
      uri: `http://localhost`,
      version: "1",
      chainId: 23295, // Sapphire Testnet
    }).toMessage();

    setSiweMsg(siweMsg);

    const signature = await window.ethereum.request({
      method: "personal_sign",
      params: [siweMsg, userAddress],
    });

    setSignature(signature);
  }

  return (
    <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
      <div className="card-body">
        <div className="flex justify-between items-start">
          <h2 className="card-title">{formatUnits(offer[0], 6)} USDC</h2>
          <div className="badge badge-success">Active</div>
        </div>
        <p className="text-sm text-gray-500">Offer ID: #{offerId}</p>
        <div className="divider my-2"></div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Status:</span>
            <span className="font-medium">{Status[offer[1]]}</span>
          </div>
        </div>

        {userAddress == lockedAddress && (
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Paypal handle:</span>
              <span className="font-medium">{"paypalHandle"}</span>
            </div>
          </div>
        )}

        <div className="flex">
          <div className="card-actions justify-end mt-4 mr-2">
            <button
              onClick={subscribeToTheOffer}
              className="btn btn-sm btn-outline"
            >
              Subscribe
            </button>
          </div>

          <SubmitEmailModal />
        </div>
      </div>
    </div>
  );
}
