const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const handlers = {};
const window = {addEventListener: (kind, fn) => { handlers[kind] = fn; }};
let copied;
const navigator = {clipboard: {writeText: async text => { copied = text; }}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../tools/browser_clipboard.js'), 'utf8'),
                   {window, navigator});
const bridge = window.CHUCKClipboard;
const settle = () => new Promise(resolve => setImmediate(resolve));
(async () => {
  const id = bridge.beginCopy('ABCD-1234-5678');
  await settle();
  assert.equal(copied, 'ABCD-1234-5678');
  assert.equal(bridge.copyStatus(id), 'copied');
  bridge.finishCopy(id);
  navigator.clipboard.writeText = async () => { throw Error('denied'); };
  const blocked = bridge.beginCopy('code');
  await settle();
  assert.equal(bridge.copyStatus(blocked), 'blocked');
  let stopped = false;
  const key = {ctrlKey:true, key:'v', stopImmediatePropagation:()=>{stopped=true;}};
  handlers.keydown(key);
  assert.equal(stopped, false);
  bridge.enablePaste(true);
  handlers.keydown(key);
  assert.equal(stopped, true);
  const event = {clipboardData:{getData:()=> 'abcd-1234-5678'},
                 preventDefault(){}, stopImmediatePropagation(){}};
  handlers.paste(event);
  assert.equal(bridge.takePaste(), 'abcd-1234-5678');
  assert.equal(bridge.takePaste(), '');
  bridge.enablePaste(false);
  handlers.paste(event);
  assert.equal(bridge.takePaste(), '');
  // The phone shell's own field hands a code in by the same door, and
  // only while the game is asking for one.
  assert.equal(bridge.isPasteEnabled(), false);
  assert.equal(bridge.offerPaste('KMW9-J6ZP-2T5D'), false);
  assert.equal(bridge.takePaste(), '');
  bridge.enablePaste(true);
  assert.equal(bridge.isPasteEnabled(), true);
  assert.equal(bridge.pastePending(), false);
  assert.equal(bridge.offerPaste('KMW9-J6ZP-2T5D'), true);
  assert.equal(bridge.pastePending(), true);
  assert.equal(bridge.takePaste(), 'KMW9-J6ZP-2T5D');
  // Pending goes false only once the game has collected it. That is the
  // handshake the shell waits on before it presses Enter.
  assert.equal(bridge.pastePending(), false);
  // Leaving the load page drops anything still waiting, so a code can
  // never arrive at a page that did not ask for one.
  bridge.offerPaste('ABCD');
  bridge.enablePaste(false);
  assert.equal(bridge.pastePending(), false);
  assert.equal(bridge.takePaste(), '');
  console.log('Browser clipboard copy, denial, paste, offer and lifecycle checks passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
