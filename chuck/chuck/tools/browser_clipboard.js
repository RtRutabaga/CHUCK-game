// Browser promises settle in JavaScript; Python polls only plain values.
(() => {
  let copyId = 0;
  const copies = new Map();
  let pasteEnabled = false;
  let pasted = "";
  window.CHUCKClipboard = {
    beginCopy(text) {
      const id = ++copyId;
      copies.set(id, "pending");
      Promise.resolve().then(() => navigator.clipboard.writeText(text)).then(
        () => { if (copies.has(id)) copies.set(id, "copied"); },
        () => { if (copies.has(id)) copies.set(id, "blocked"); }
      );
      return id;
    },
    copyStatus(id) { return copies.get(id) || "blocked"; },
    finishCopy(id) { copies.delete(id); },
    enablePaste(enabled) { pasteEnabled = enabled; pasted = ""; },
    takePaste() { const text = pasted; pasted = ""; return text; }
  };
  // Let the browser perform Ctrl/Cmd-V, instead of SDL cancelling it.
  window.addEventListener("keydown", event => {
    if (pasteEnabled && (event.ctrlKey || event.metaKey) &&
        event.key.toLowerCase() === "v") {
      event.stopImmediatePropagation();
    }
  }, true);
  window.addEventListener("paste", event => {
    if (!pasteEnabled) return;
    pasted = event.clipboardData?.getData("text/plain") || "";
    event.preventDefault();
    event.stopImmediatePropagation();
  }, true);
})();
