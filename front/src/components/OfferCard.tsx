import SubmitEmailModal from "./SubmitEmailModal";

export default function OfferCard({ offer }) {
  return (
    <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
      <div className="card-body">
        <div className="flex justify-between items-start">
          <h2 className="card-title">
            {offer.amount} {offer.token}
          </h2>
          <div className="badge badge-success">Active</div>
        </div>
        <p className="text-sm text-gray-500">Offer ID: #{offer.id}</p>
        <div className="divider my-2"></div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Status:</span>
            <span className="font-medium">{offer.status}</span>
          </div>
          <div className="flex justify-between">
            <span>Locked Funds:</span>
            <span className="font-medium">
              {offer.locked} {offer.token}
            </span>
          </div>
        </div>
        <div className="card-actions justify-end mt-4">
          <button className="btn btn-sm btn-outline">Release Funds</button>
        </div>
        <SubmitEmailModal />
      </div>
    </div>
  );
}
