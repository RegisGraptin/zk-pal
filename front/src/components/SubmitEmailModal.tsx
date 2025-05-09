import { useState } from "react";

export default function SubmitEmailModal() {
  const [showModal, setShowModal] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file ? file.name : null); // Store file name in state
  };

  const generateZKProof = () => {
    console.log("Generate ZK email proof");
  };

  return (
    <>
      {showModal && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">
              Upload your email to prove it
            </h3>
            <div>
              <label
                htmlFor="uploadFile"
                className="pt-10 bg-[#1f1f1f] text-gray-300 font-semibold text-base rounded h-52 flex flex-col items-center justify-center cursor-pointer border-2 border-dashed border-gray-600 mx-auto font-[sans-serif] transition hover:border-primary"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-11 mb-2 fill-gray-400"
                  viewBox="0 0 32 32"
                >
                  <path d="M23.75 11.044a7.99 7.99 0 0 0-15.5-.009A8 8 0 0 0 9 27h3a1 1 0 0 0 0-2H9a6 6 0 0 1-.035-12 1.038 1.038 0 0 0 1.1-.854 5.991 5.991 0 0 1 11.862 0A1.08 1.08 0 0 0 23 13a6 6 0 0 1 0 12h-3a1 1 0 0 0 0 2h3a8 8 0 0 0 .75-15.956z" />
                  <path d="M20.293 19.707a1 1 0 0 0 1.414-1.414l-5-5a1 1 0 0 0-1.414 0l-5 5a1 1 0 0 0 1.414 1.414L15 16.414V29a1 1 0 0 0 2 0V16.414z" />
                </svg>

                {selectedFile ? (
                  <p className="text-sm font-medium text-gray-600 mt-2">
                    {selectedFile}
                  </p>
                ) : (
                  <p className="text-sm text-gray-300">Upload your email</p>
                )}

                <input
                  type="file"
                  id="uploadFile"
                  className="hidden"
                  name="uploadFile"
                  onChange={handleFileChange}
                />

                <p className="text-xs text-gray-500 mt-2">
                  Select your email file (EML...)
                </p>
              </label>

              <div className="modal-action">
                <button
                  type="button"
                  className="flex-1 py-3 rounded-lg font-medium transition-all bg-gray-600 hover:bg-gray-700"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>

                <button
                  onClick={generateZKProof}
                  disabled={!selectedFile}
                  className={`flex-1 py-3 rounded-lg font-medium transition-all ${
                    selectedFile
                      ? "bg-blue-600 hover:bg-blue-700"
                      : "bg-gray-700 cursor-not-allowed"
                  }`}
                >
                  Upload Email
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card-actions justify-end mt-4">
        <button
          onClick={() => setShowModal(true)}
          className="btn btn-sm btn-outline"
        >
          Email Proof
        </button>
      </div>
    </>
  );
}
