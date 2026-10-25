import { looksLikeReceipt } from "./frijolito.js";

chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  chrome.contextMenus.create({ id: "ask", title: "Ask Frijolito about \"%s\"", contexts: ["selection"] });
  chrome.contextMenus.create({ id: "verify", title: "Verify with Frijolito", contexts: ["selection"] });
});

// The panel opens on the click itself (it needs the user gesture), then reads
// the hand-off from session storage, which it also watches while open.
chrome.contextMenus.onClicked.addListener((info, tab) => {
  const text = (info.selectionText || "").trim().slice(0, 1500);
  if (!text) return;
  chrome.sidePanel.open({ windowId: tab.windowId });
  const mode = info.menuItemId === "verify" || looksLikeReceipt(text) ? "verify" : "ask";
  chrome.storage.session.set({ handoff: { mode, text, at: Date.now() } });
});
