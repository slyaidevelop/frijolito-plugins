// Talks to Frijolito Core's two public endpoints. Both are unauthenticated by
// design: the concierge only knows curated public facts, and verification is
// permissionless. Nothing here reads the page the person is on.
export const ORIGIN = "https://frijolito.app";

const RECEIPT_ID = /\bFJ2?-[A-Za-z0-9-]{6,}\b/;
const RECEIPT_HASH = /\b[0-9a-f]{64}\b/;

export function looksLikeReceipt(text) {
  return RECEIPT_ID.test(text) || RECEIPT_HASH.test(text.toLowerCase());
}

// Pulls the first receipt reference out of a selection or a pasted line.
export function receiptReference(text) {
  const id = text.match(RECEIPT_ID);
  if (id) return { receipt_id: id[0] };
  const hash = text.toLowerCase().match(RECEIPT_HASH);
  return hash ? { receipt_hash: hash[0] } : null;
}

async function post(path, body) {
  const res = await fetch(`${ORIGIN}/functions/${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 429) throw new Error(data.error || "Let's slow down a little. Try again in a minute.");
  if (!res.ok && !data.verdict) throw new Error(data.detail || data.error || "Frijolito is unavailable right now.");
  return data;
}

export const ask = (messages, seen) => post("coreConcierge", { messages, seen });
export const verify = (ref) => post("verify_receipt", ref);
