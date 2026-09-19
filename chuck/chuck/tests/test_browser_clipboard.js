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
  console.log('Browser clipboard copy, denial, paste and lifecycle checks passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
