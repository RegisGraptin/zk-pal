import { FormEvent, useState } from "react";
// import { generateEmailVerifierInputs } from "@zk-email/helpers";
// import { verifyDKIMSignature } from "@zk-email/helpers/dist/dkim";

import { UltraHonkBackend } from "@aztec/bb.js";
import { Noir } from "@noir-lang/noir_js";
import circuit from "../data/circuits.json";

type BoundedVecInput = {
  storage: number[]; // u8 array (or other type if T ≠ u8)
  len: number; // u32 length of actual data
};

type RSAPubkey = {
  modulus: string[]; // each string represents a Field element
  redc: string[];
};

function convertToRSAPubkey(inputArray: string[]): RSAPubkey {
  // Convert the input array of strings to an array of BigInts (modulus elements)
  const modulus = inputArray.map((str) => str); // Convert each element to BigInt

  // Placeholder for redc calculation - This should ideally be calculated based on the modulus
  // For now, we're just setting it as an array of the same length (in real use, we need the Montgomery reduction)
  const redc = modulus; // This is just a placeholder; calculate Montgomery constant if needed

  // Return the RSAPubkey struct (you might need to adapt it based on how the struct is defined in your system)
  return {
    modulus, // An array of BigInts representing the modulus
    redc, // An array (placeholder here) - Ideally, calculate redc properly using the modulus
  };
}

function toBoundedVec(input: string | Uint8Array): {
  storage: number[];
  len: number;
} {
  const bytes =
    typeof input === "string" ? new TextEncoder().encode(input) : input;

  return {
    storage: Array.from(bytes),
    len: bytes.length,
  };
}

export default function SubmitEmailModal() {
  const [showModal, setShowModal] = useState(false);

  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      setSelectedFile(file ? file.name : null); // Store file name in state
  };

  async function getFileContentAsString(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);

    // Extract the email content
    const file = formData.get("uploadFile") as File;
    const content = await getFileContentAsString(file);

    console.log(content);

    // const inputParams = {
    //   maxBodyLength: 25216, // Required to avoid exceeding ZK circuit limit
    // };

    // FIXME: ZKEmail is relying on node:Buffer
    // Which cannot be used on the frontend side...

    // const verifier = await generateEmailVerifierInputs(content, inputParams);

    // console.log("Prepare data...");
    // console.log(verifier);

    // let dkim = await verifyDKIMSignature(content);
    // console.log(dkim.headers);

    // try {
    //   console.log("Loading noir circuit");
    //   const noir = new Noir(circuit);
    //   const backend = new UltraHonkBackend(circuit.bytecode);

    //   console.log("Backend ready");

    //   const KEY_LIMBS = 17;

    //   verifier.pubkey.push("0");

    //   // const rsaPubkey = {
    //   //   modulus: verifier.pubkey!.slice(0, KEY_LIMBS),
    //   //   redc: verifier.pubkey!.slice(KEY_LIMBS, 2 * KEY_LIMBS),
    //   // };

    //   // console.log(rsaPubkey);

    //   // verifier.pubkey.push("0");
    //   console.log(verifier.pubkey);
    //   console.log(convertToRSAPubkey(verifier.pubkey));

    //   verifier.signature.push("0");

    //   const inputs = {
    //     header: toBoundedVec(verifier.emailHeader!),
    //     body: toBoundedVec(verifier.emailBody!),
    //     pubkey: convertToRSAPubkey(verifier.pubkey),
    //     signature: verifier.signature!,
    //   };
    //   console.log(inputs);

    //   const { witness } = await noir.execute(inputs);
    // } catch (e) {
    //   console.log("Issue");
    //   console.log(e);
    // }

    // console.log(toHex(verifier.emailBody));

    // Generate a zk proof
  }

  //   const generateZKProof = () => {
  //     console.log("Generate ZK email proof");

  //     const parser = new MimeParser();

  //     parser.onheader = (node) => {
  //       const dkim = node.headers.get("dkim-signature")?.initial;
  //       if (dkim) {
  //         console.log("DKIM-Signature:", dkim);
  //       } else {
  //         console.warn("No DKIM-Signature found.");
  //       }
  //     };

  //     parser.write(arrayBuffer);
  //     parser.end();
  //   };

  return (
    <>
      {showModal && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">
              Upload your email to prove it
            </h3>
            <form onSubmit={onSubmit}>
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
            </form>
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
