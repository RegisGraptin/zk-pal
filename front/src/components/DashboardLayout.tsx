"use client";

import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useState } from "react";
import CreateOfferModal from "./CreateOfferModal";
import OfferCard from "./OfferCard";
import { getAddress } from "viem";

import Escrow from "@/data/Escrow.json";
import { useReadContract, useReadContracts } from "wagmi";

export default function DashboardLayout() {
  const [showModal, setShowModal] = useState(false);

  // Read all the entries available
  const { data: activeEntries, refetch: refetchEntries } = useReadContract({
    address: getAddress(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS!),
    abi: Escrow.abi,
    functionName: "getActiveEntries",
    args: [],
  });

  const { data: entries } = useReadContracts({
    contracts: Array.from(activeEntries ? (activeEntries as []) : []).map(
      (index, _) => ({
        abi: Escrow.abi,
        address: getAddress(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS!),
        functionName: "getEntry",
        args: [index],
      })
    ),
  });

  console.log("activeEntries:", activeEntries);
  console.log("entries:", entries);

  const [offers] = useState([
    { id: 1, amount: 50, token: "USDC", status: "Pending", locked: 50 },
    { id: 2, amount: 100, token: "USDT", status: "Completed", locked: 0 },
  ]);

  return (
    <div className="min-h-screen bg-base-200">
      <div className="navbar container mx-auto bg-base-100 shadow-lg mb-4">
        <div className="flex-1">
          <h1 className="text-xl font-bold ml-2">
            {process.env.NEXT_PUBLIC_SITE_NAME}
          </h1>
        </div>
        <div className="flex-none">
          <ConnectButton />
        </div>
      </div>

      <div className="container mx-auto p-4">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-semibold">Your Offers</h2>
          <label
            htmlFor="create-offer-modal"
            className="btn btn-primary modal-button"
            onClick={() => setShowModal(true)}
          >
            Create New Offer
          </label>
        </div>
        {showModal && (
          <CreateOfferModal
            onClose={() => {
              setShowModal(false);
              refetchEntries();
            }}
          />
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {(activeEntries as []) &&
            (entries as []) &&
            activeEntries.map((id, index) => (
              <OfferCard key={id} offerId={id} offer={entries[index].result} />
            ))}
        </div>
      </div>
    </div>
  );
}
