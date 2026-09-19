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
    // Whether the game currently has a code field open. The load page
    // turns paste on for its own reasons; the mobile shell reads the
    // same flag from the parent document to know when to offer its
    // keyboard, rather than the game growing a second way to say so.
    isPasteEnabled() { return pasteEnabled; },
    // A code from somewhere that is not the system clipboard: the touch
    // shell's own field, typed on the phone's keyboard. It arrives by
    // the same door a real paste does, and only while the game is
    // asking, so there is one way in and one thing to reason about.
    offerPaste(text) {
      if (!pasteEnabled) return false;
      pasted = String(text == null ? "" : text);
      return true;
    },
    // Whether something is still waiting to be collected. The shell
    // presses Enter only once this goes false: the game reads key
    // events before it polls for a paste, so an Enter sent in the same
    // breath would arrive at a field that is still empty.
    pastePending() { return pasted !== ""; },
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
