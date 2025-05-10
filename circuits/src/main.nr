use sha256::sha256_var;
use std::{collections::bounded_vec::BoundedVec, hash::pedersen_hash};
use zkemail::{
    dkim::RSAPubkey, headers::body_hash::get_body_hash, KEY_LIMBS_2048, Sequence
};

global MAX_EMAIL_HEADER_LENGTH: u32 = 1024;
global MAX_EMAIL_BODY_LENGTH: u32 = 25280;

fn main(
    header: BoundedVec<u8, MAX_EMAIL_HEADER_LENGTH>,
    body: BoundedVec<u8, MAX_EMAIL_BODY_LENGTH>,
    pubkey: RSAPubkey<KEY_LIMBS_2048>,
    signature: [Field; KEY_LIMBS_2048],
    // body_hash_index: u32,
    // dkim_header_sequence: Sequence,
) -> pub [Field; 2] {
     // check the body and header lengths are within bounds
    assert(header.len() <= MAX_EMAIL_HEADER_LENGTH);
    assert(body.len() <= MAX_EMAIL_BODY_LENGTH);

    // ~ 86,553 constraints
    // verify the dkim signature over the header
    pubkey.verify_dkim_signature(header, signature);

    // // ~ 6,289 constraints
    // // extract the body hash from the header
    // let signed_body_hash = get_body_hash(header, dkim_header_sequence, body_hash_index);

    // // ~ 113,962 constraints
    // // hash the asserted body
    // let computed_body_hash: [u8; 32] = sha256_var(body.storage, body.len() as u64);

    // // compare the body hashes
    // assert(
    //     signed_body_hash == computed_body_hash,
    //     "SHA256 hash computed over body does not match body hash found in DKIM-signed header",
    // );

    // ~ 10,255 constraints
    // hash the pubkey and signature for the standard outputs
    let email_nullifier = pedersen_hash(signature);
    [pubkey.hash(), email_nullifier]
}

#[test]
fn test_main() {

    // main(
    //     header,
    //     body, 
    //     pubKey,
    //     signature,
    //     431,
    //     dkim
    // );

    // Uncomment to make test fail
    // main(1, 1);
}
