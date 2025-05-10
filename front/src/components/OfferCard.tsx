import { formatUnits, getAddress } from "viem";
import SubmitEmailModal from "./SubmitEmailModal";
import { useWriteContract } from "wagmi";

import Escrow from "@/data/Escrow.json";

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
