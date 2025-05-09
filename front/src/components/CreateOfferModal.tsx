import { useEffect, useRef, useState } from "react";
import { erc20Abi, getAddress, parseUnits } from "viem";
import { useWaitForTransactionReceipt, useWriteContract } from "wagmi";

export default function CreateOfferModal({ onClose }) {
  const [isApproved, setIsApproved] = useState(false);

  const [formData, setFormData] = useState({
    amount: "",
    token: "USDC",
    paypalEmail: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
  };

  const { writeContract, data: txHashApprove, isPending } = useWriteContract();

  const { isLoading: isTxLoading, isSuccess: isTxSuccess } =
    useWaitForTransactionReceipt({
      hash: txHashApprove,
    });

  useEffect(() => {
    if (isTxSuccess && isApproved) {
      // Succeed to lock account
      onClose();
    }

    if (isTxSuccess && !isApproved) {
      // Approve the tx
      setIsApproved(true);
    }
  }, [isTxSuccess]);

  const handleApprove = async () => {
    writeContract({
      address: getAddress(process.env.NEXT_PUBLIC_USDC_ADDRESS!),
      abi: erc20Abi,
      functionName: "approve",
      args: [
        getAddress(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS!),
        parseUnits(formData.amount, 6), // USDC has 6 decimals
      ],
    });
  };

  const handleSend = async () => {
    // FIXME: Wait for smart contract ready & ABI
    // writeContract({
    //   address: getAddress(process.env.NEXT_PUBLIC_ASSET_ADDRESS!),
    //   abi: erc20Abi,
    //   functionName: "send",
    //   args: [
    //     getAddress(process.env.NEXT_PUBLIC_CONFIDENTIAL_LAYER_ADDRESS!),
    //     parseUnits(formData.amount, 6), // USDC has 6 decimals
    //   ],
    // });

    // FIXME: to be removed
    onClose();
  };

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        <h3 className="font-bold text-lg mb-4">Create New Offer</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-control">
            <label className="label">
              <span className="label-text">Amount to Receive</span>
            </label>
            <input
              type="number"
              placeholder="50"
              className="input input-bordered"
              value={formData.amount}
              onChange={(e) =>
                setFormData({ ...formData, amount: e.target.value })
              }
              required
            />
          </div>

          <div className="form-control mt-4">
            <label className="label">
              <span className="label-text">Token to Lock: USDC</span>
            </label>
          </div>

          <div className="form-control mt-4">
            <label className="label">
              <span className="label-text">PayPal Email</span>
            </label>
            <input
              type="email"
              placeholder="your@paypal.com"
              className="input input-bordered"
              value={formData.paypalEmail}
              onChange={(e) =>
                setFormData({ ...formData, paypalEmail: e.target.value })
              }
              required
            />
          </div>

          <div className="modal-action">
            <button
              type="button"
              className="flex-1 py-3 rounded-lg font-medium transition-all bg-gray-600 hover:bg-gray-700"
              onClick={onClose}
            >
              Cancel
            </button>

            {/* Approve button */}
            {!isApproved ? (
              <button
                onClick={handleApprove}
                disabled={!formData.amount || isPending || isTxLoading}
                className={`flex-1 py-3 rounded-lg font-medium transition-all ${
                  formData.amount && !isPending && !isTxLoading
                    ? "bg-blue-600 hover:bg-blue-700"
                    : "bg-gray-700 cursor-not-allowed"
                }`}
              >
                {isTxLoading || isPending ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="animate-spin">🌀</span>
                    Approving...
                  </span>
                ) : (
                  "Approve USDC"
                )}
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!formData.amount || isPending || isTxLoading}
                className={`flex-1 py-3 rounded-lg font-medium transition-all ${
                  formData.amount && !isPending && !isTxLoading
                    ? "bg-blue-600 hover:bg-blue-700"
                    : "bg-gray-700 cursor-not-allowed"
                }`}
              >
                {isTxLoading || isPending ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="animate-spin">🌀</span>
                    Sending...
                  </span>
                ) : (
                  "Send USDC"
                )}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
