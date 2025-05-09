import { useState } from "react";

export default function CreateOfferModal({ onClose }) {
  const [formData, setFormData] = useState({
    amount: "",
    token: "USDC",
    paypalEmail: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle form submission here
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
              <span className="label-text">Token to Lock</span>
            </label>
            <select
              className="select select-bordered"
              value={formData.token}
              onChange={(e) =>
                setFormData({ ...formData, token: e.target.value })
              }
            >
              <option>USDC</option>
              <option>USDT</option>
              <option>DAI</option>
            </select>
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
            <button type="button" className="btn" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create Offer
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
