import { ORIGIN, ask, verify, receiptReference } from "./frijolito.js";

const log = document.getElementById("log");
const hello = document.getElementById("hello");
const form = document.getElementById("say");
const text = document.getElementById("text");
const send = document.getElementById("send");

// The conversation lives for the browser session only, never on disk.
let items = [];
let seen = [];
let busy = false;

const el = (tag, props = {}, ...kids) => {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...kids.filter(Boolean));
  return node;
};
const link = (href, label) => {
  const url = href.startsWith("/") ? ORIGIN + href : href;
  return el("a", { href: url, target: "_blank", rel: "noopener", textContent: label });
};
const pretty = (href) => (href.startsWith("/") ? href.slice(1).replace(/-/g, " ") : new URL(href).hostname);
const day = (iso) => (iso ? new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) : "");

function renderLito(a) {
  const node = el("div", { className: "msg lito" });
  for (const para of a.reply.split(/\n{2,}/)) node.append(el("p", { textContent: para }));
  if (a.steps?.length) node.append(el("ol", {}, ...a.steps.map((s) => el("li", { textContent: s }))));
  if (a.highlight) node.append(el("blockquote", { textContent: a.highlight }));
  if (a.links?.length) node.append(el("div", { className: "links" }, ...a.links.map((h) => link(h, pretty(h)))));
  return node;
}

function renderReceipt({ ref, result }) {
  const id = result.receipt_id || ref.receipt_id || ref.receipt_hash;
  const v = result.verdict || "UNKNOWN";
  const box = el("div", { className: `msg receipt ${v}` }, el("div", { className: "verdict", textContent: v }));
  if (v === "VALID") {
    const outside = String(result.receipt_id || "").startsWith("FJ2-");
    box.append(el("h2", { textContent: result.moment_label || (result.receipt_kind || "Receipt").replace(/[_.]/g, " ") }));
    const rows = [];
    for (const p of result.parties || []) rows.push([p.role || "Party", p.label]);
    if (result.created_at) rows.push(["Made", day(result.created_at)]);
    if (result.status && result.status !== "active") rows.push(["Status", result.status]);
    rows.push(["Witness", outside ? "Seen from outside" : "Reported by an app, signed by Frijolito"]);
    rows.push(["Sealed", result.root ? `Daily root #${result.root.root_seq}${result.root.anchor_status === "confirmed" ? ", in Bitcoin" : ""}` : "Not yet, sealed nightly"]);
    if (result.demo) rows.push(["Note", "Demo receipt"]);
    box.append(el("dl", {}, ...rows.flatMap(([k, val]) => [el("dt", { textContent: k }), el("dd", { textContent: val })])));
    if (["expired", "revoked"].includes(result.status)) box.append(el("p", { className: "say", textContent: `Genuine, but ${result.status}. It no longer stands.` }));
  } else if (v === "INVALID") {
    box.append(el("h2", { textContent: "Don't trust this receipt" }), el("p", { className: "say", textContent: result.detail || "It fails Frijolito's checks." }));
  } else {
    box.append(el("h2", { textContent: "Frijolito never made this one" }), el("p", { className: "say", textContent: "It's well formed, but there's no record of it. That isn't proof it's fake, and it isn't proof it's real." }));
  }
  box.append(el("p", { className: "say" }, el("code", { textContent: id })));
  if (v !== "UNKNOWN" && result.receipt_id) box.append(link(`/verify/${result.receipt_id}`, "Open the full proof"));
  return box;
}

function render() {
  hello.hidden = items.length > 0;
  log.replaceChildren(hello);
  items.forEach((item, i) => {
    if (item.kind === "me") log.append(el("div", { className: "msg me", textContent: item.text }));
    if (item.kind === "lito") {
      const node = renderLito(item.answer);
      if (i === items.length - 1 && !busy && item.answer.options?.length) {
        node.append(el("div", { className: "chips" }, ...item.answer.options.map((o) => el("button", { type: "button", textContent: o, onclick: () => submit(o) }))));
      }
      log.append(node);
    }
    if (item.kind === "receipt") log.append(renderReceipt(item));
    if (item.kind === "error") log.append(el("div", { className: "msg lito error", textContent: item.text }));
  });
  if (busy) log.append(el("div", { className: "msg lito dots" }, el("i"), el("i"), el("i")));
  log.scrollTop = log.scrollHeight;
  chrome.storage.session.set({ items, seen });
}

async function submit(raw, mode) {
  const said = raw.trim();
  if (!said || busy) return;
  text.value = "";
  resize();
  const ref = mode !== "ask" ? receiptReference(said) : null;
  items.push({ kind: "me", text: said });
  busy = true;
  render();
  try {
    if (ref) {
      items.push({ kind: "receipt", ref, result: await verify(ref) });
    } else if (mode === "verify") {
      items.push({ kind: "error", text: "That doesn't look like a receipt. Receipt IDs start with FJ- or FJ2-." });
    } else {
      const messages = items
        .filter((m) => m.kind === "me" || m.kind === "lito")
        .map((m) => (m.kind === "me" ? { role: "user", content: m.text } : { role: "assistant", content: m.answer.reply }));
      const answer = await ask(messages, seen);
      if (answer.card && answer.card !== "none") seen = [...new Set([answer.card, ...seen])].slice(0, 6);
      items.push({ kind: "lito", answer });
    }
  } catch (error) {
    items.push({ kind: "error", text: error.message || "Frijolito is unavailable right now." });
  }
  busy = false;
  render();
  text.focus();
}

function resize() {
  text.style.height = "auto";
  text.style.height = `${Math.min(text.scrollHeight, 140)}px`;
  send.disabled = !text.value.trim();
}

form.addEventListener("submit", (e) => { e.preventDefault(); submit(text.value); });
text.addEventListener("input", resize);
text.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); submit(text.value); }
});

// Text sent from the right-click menu arrives through session storage.
async function takeHandoff() {
  const { handoff } = await chrome.storage.session.get("handoff");
  if (!handoff) return;
  await chrome.storage.session.remove("handoff");
  submit(handoff.mode === "verify" ? handoff.text : `About this: "${handoff.text}"`, handoff.mode);
}
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "session" && changes.handoff?.newValue) takeHandoff();
});

chrome.storage.session.get(["items", "seen"]).then((saved) => {
  items = saved.items || [];
  seen = saved.seen || [];
  render();
  takeHandoff();
  text.focus();
});
