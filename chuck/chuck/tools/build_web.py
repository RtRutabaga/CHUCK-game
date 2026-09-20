"""Stage a browser-only copy, then package it with Pygbag.

Run from any directory: python tools/build_web.py
Add --serve to build and serve locally at http://127.0.0.1:8000.
Desktop WAV masters and save files are never included or modified.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "build" / "browser-app"


def finalize_web_artifact(web: Path) -> None:
    """Apply CHUCK's host-specific additions to Pygbag's static output."""
    page = web / "index.html"
    html = page.read_text(encoding="utf-8")
    archive = web / "browser-app.apk"
    # A new URL for changed game bytes prevents browsers reusing an old APK
    # after fetching a newer index. Keep the legacy file for older index pages.
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()[:16]
    versioned = archive.with_name(f"browser-app-{digest}.apk")
    shutil.copyfile(archive, versioned)
    html = html.replace("browser-app.apk", versioned.name)
    # Override the stock template's independent width/height scaling. SDL
    # retains a fixed framebuffer; CSS fits it into the browser viewport.
    style = """<style>
html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #000 !important; }
#canvas { width: min(100vw, 177.777778vh) !important;
          height: min(100vh, 56.25vw) !important;
          position: fixed !important; inset: 0 !important;
          margin: auto !important; border: 0 !important;
          image-rendering: pixelated; }
#mobile-link { position: fixed; left: 50%; bottom: 6px; z-index: 10;
          transform: translateX(-50%);
          font: 500 12px/1 system-ui, sans-serif; color: #ffffff8c;
          text-decoration: none; background: #0d0a16b3;
          border: 1px solid #ffffff2b; border-radius: 999px;
          padding: 6px 12px; }
#mobile-link:hover { color: #fff; border-color: #ffffff66; }
</style>"""
    scripts = "".join(
        "<script>" + Path(__file__).with_name(name).read_text(encoding="utf-8")
        + "</script>"
        # Audio first: the session type should be declared before the
        # wasm build boots and creates an audio context.
        for name in ("browser_audio.js", "browser_clipboard.js"))
    page.write_text(html + style + MOBILE_POINTER + scripts, encoding="utf-8")
    mobile = web / "mobile"
    mobile.mkdir(exist_ok=True)
    (mobile / "index.html").write_text(MOBILE_SHELL, encoding="utf-8")
    # Added to the home screen, the shell launches without browser bars.
    # That is the only way to lose them on an iPhone, where Safari has no
    # Fullscreen API; Android honours the orientation as well.
    (mobile / "manifest.webmanifest").write_text(json.dumps({
        "name": "CHUCK",
        "short_name": "CHUCK",
        "display": "fullscreen",
        "orientation": "landscape",
        "start_url": "./",
        "scope": "./",
        "background_color": "#09070d",
        "theme_color": "#09070d",
    }, indent=2), encoding="utf-8")
    # Pages otherwise runs Jekyll, which can omit Pygbag runtime files whose
    # names begin with an underscore.
    (web / ".nojekyll").touch()


# The desktop page's one nod to the phone: a way to find `/mobile/`,
# since nothing here detects a device. A link rather than a redirect --
# user-agent sniffing would have to be right about the Xbox browser,
# and being wrong there drops a controller player into a touch shell.
#
# It removes itself inside a frame, because `/mobile/` embeds this very
# page. Left alone it would sit inside the touch shell offering to take
# the player to the touch shell. The frame check is the reliable half;
# `?mobile=1`, which the shell already appends, says the same thing out
# loud.
MOBILE_POINTER = """<a id="mobile-link" href="mobile/">On a phone? Touch controls</a>
<script>
if (window.top !== window.self || location.search.indexOf("mobile=1") >= 0) {
  document.getElementById("mobile-link").remove();
}
</script>"""

# A landscape touch shell for phones: an iframe around the same browser
# build, with buttons that press the keys the game already binds.
#
# The buttons dispatch at the iframe's *document*, not its window, because
# that is where SDL registers keydown/keyup -- an event sent to the window
# is never seen. Each button also carries an explicit `code`, since SDL2
# looks the scancode up from it, so "f" must travel as "KeyF".
MOBILE_SHELL = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no"><title>CHUCK — mobile test</title><link rel="manifest" href="manifest.webmanifest"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="CHUCK"><meta name="theme-color" content="#09070d">
<style>
/* --scale multiplies the sizes rather than stretching the clamp
   bounds. Widening the bounds did almost nothing on a phone: at
   these viewports the floor wins, so the slider moved a button by
   half a pixel and the d-pad, on its own variable, not at all. */
:root{--scale:1;--button:calc(clamp(52px,13vmin,92px) * var(--scale));--pad:calc(clamp(150px,36vmin,250px) * var(--scale));--chip:calc(46px * var(--scale));--edge:clamp(12px,4vmin,40px)}
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#09070d;color:#fff;font:600 14px system-ui,sans-serif;touch-action:none;-webkit-user-select:none;user-select:none}
#game{position:fixed;inset:0;width:100%;height:100%;border:0;background:#000}
#controls{position:fixed;inset:0;pointer-events:none;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
.touch{pointer-events:auto;position:absolute;border:1px solid #ffffff55;background:#241d38cc;color:#fff;backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);display:grid;place-items:center;min-width:var(--button);min-height:var(--button);font:700 calc(clamp(11px,2.5vmin,16px) * var(--scale)) system-ui;border-radius:50%;box-shadow:0 2px 10px #0008}
.touch:active,.touch.held{background:#7954a9dd;transform:scale(.96)}
#pad{position:absolute;pointer-events:auto;left:calc(var(--edge) + env(safe-area-inset-left));bottom:calc(var(--edge) + env(safe-area-inset-bottom));width:var(--pad);height:var(--pad);display:grid;grid-template:repeat(3,1fr)/repeat(3,1fr);gap:4px;background:#241d3866;border-radius:24%;touch-action:none}
#pad .touch{position:static;width:100%;height:100%;min-width:0;min-height:0;border-radius:22%;font-size:calc(clamp(20px,5vmin,38px) * var(--scale));pointer-events:none}
#up{grid-area:1/2}#left{grid-area:2/1}#down{grid-area:3/2}#right{grid-area:2/3}
#actions{position:absolute;pointer-events:auto;right:calc(var(--edge) + env(safe-area-inset-right));bottom:calc(var(--edge) + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(2,var(--button));grid-auto-rows:var(--button);gap:10px}
#actions .touch{position:static;width:100%;height:100%}
#actions #jump{grid-area:2/2}#actions #scratch{grid-area:2/1}#actions #inspect{grid-area:1/2}
#pause{right:calc(var(--edge) + env(safe-area-inset-right));top:calc(var(--edge) + env(safe-area-inset-top));min-width:var(--chip);min-height:var(--chip);border-radius:18px}
#settings{left:calc(var(--edge) + env(safe-area-inset-left));top:calc(var(--edge) + env(safe-area-inset-top));min-width:var(--chip);min-height:var(--chip);border-radius:18px}
#fullscreen{left:calc(var(--edge) + env(safe-area-inset-left) + 56px);top:calc(var(--edge) + env(safe-area-inset-top));min-width:var(--chip);min-height:var(--chip);border-radius:18px}
#panel{display:none;position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(88vw,360px);padding:20px;background:#171322f5;border:1px solid #ffffff55;border-radius:14px;pointer-events:auto;line-height:1.5;box-shadow:0 8px 30px #000b}
#panel.open{display:block}#panel h1{font-size:18px;margin:0 0 12px}#panel label{display:block;margin:12px 0}#panel input{width:100%;accent-color:#ad80dc}#close{float:right;border:0;background:#ffffff22;color:white;border-radius:8px;padding:5px 10px}
#rotate{position:fixed;inset:0;z-index:30;display:none;place-items:center;text-align:center;padding:24px;background:#09070df5;color:#f6d68c;font:600 clamp(13px,4vmin,20px)/1.6 system-ui}
#rotate span{display:block;color:#ffffffa0;font-weight:400;margin-top:8px}
@media (orientation:portrait){#rotate{display:grid}}
#code{position:absolute;inset:0;pointer-events:none;display:none}
#code.open{display:block}
#codebox{pointer-events:auto;position:absolute;left:50%;transform:translateX(-50%);top:calc(8px + env(safe-area-inset-top));width:min(94vw,520px);padding:12px 14px;background:#171322f5;border:1px solid #ffffff55;border-radius:14px;box-shadow:0 8px 30px #000b;line-height:1.4}
#codebox h1{margin:0 0 9px;font-size:13px;letter-spacing:.07em;text-transform:uppercase;color:#f6d68c}
#codefield{width:100%;padding:10px 6px;border:1px solid #ffffff55;border-radius:9px;background:#0d0a16;color:#f6d68c;text-align:center;text-transform:uppercase;letter-spacing:.16em;font:700 clamp(16px,4.4vmin,26px)/1.25 ui-monospace,SFMono-Regular,Menlo,monospace;-webkit-user-select:text;user-select:text;touch-action:auto}
#codebuttons{display:flex;gap:8px;margin-top:10px}
#codebuttons button{flex:1;padding:12px 6px;border:1px solid #ffffff55;border-radius:9px;background:#3a2f57;color:#fff;font:700 clamp(11px,2.7vmin,15px) system-ui}
#codebuttons button:active,#codeload.held{background:#7954a9dd}
#codeload{background:#4d3f77}
#codenote{margin:9px 0 0;font-weight:400;font-size:11px;opacity:.75}
</style></head><body><div id="rotate"><div>Turn your phone sideways.<span>CHUCK is a landscape game.</span></div></div><iframe id="game" src="../index.html?mobile=1" allow="clipboard-read; clipboard-write" title="CHUCK game"></iframe><div id="controls">
<div id="pad"><button class="touch" data-pad id="up" data-key="ArrowUp" data-code="ArrowUp" data-keycode="38" aria-label="Move up">▲</button><button class="touch" data-pad id="left" data-key="ArrowLeft" data-code="ArrowLeft" data-keycode="37" aria-label="Move left">◀</button><button class="touch" data-pad id="down" data-key="ArrowDown" data-code="ArrowDown" data-keycode="40" aria-label="Move down">▼</button><button class="touch" data-pad id="right" data-key="ArrowRight" data-code="ArrowRight" data-keycode="39" aria-label="Move right">▶</button></div>
<div id="actions"><button class="touch" id="jump" data-key=" " data-code="Space" data-keycode="32" aria-label="Jump">JUMP</button><button class="touch" id="scratch" data-key="f" data-code="KeyF" data-keycode="70" aria-label="Scratch">SCRATCH</button><button class="touch" id="inspect" data-key="e" data-code="KeyE" data-keycode="69" aria-label="Inspect or talk">INSPECT<br>/ TALK</button></div>
<button class="touch" id="pause" data-key="Escape" data-code="Escape" data-keycode="27" aria-label="Pause">Ⅱ</button><button class="touch" id="settings" aria-label="Control settings">⚙</button><button class="touch" id="fullscreen" aria-label="Full screen">⛶</button>
<div id="panel"><button id="close">Close</button><h1>Touch controls</h1><label>Control size <input id="size" type="range" min="70" max="140" value="100"></label><label>Left / right inset <input id="inset" type="range" min="0" max="70" value="40"></label><p>Keep fingers on the edges so the gameplay view stays clear.</p><p id="installnote">On iPhone there is no full-screen button: Safari does not offer one. Use <b>Share → Add to Home Screen</b>, then open CHUCK from that icon — it launches with no browser bars at all.</p></div>
<div id="code"><div id="codebox"><h1>Load a save code</h1><input id="codefield" type="text" inputmode="text" autocapitalize="characters" autocorrect="off" autocomplete="off" spellcheck="false" maxlength="16" placeholder="XXXX-XXXX-XXXX" aria-label="Save code"><div id="codebuttons"><button id="codepaste">PASTE</button><button id="codeload" data-key="Enter" data-code="Enter" data-keycode="13" aria-label="Load this code">LOAD</button><button id="codehide">HIDE</button></div><p id="codenote"></p></div></div></div>
<script>
const frame=document.getElementById('game'); const active=new Map();
function key(button,down){const doc=frame.contentDocument; if(!doc)return; const n=+button.dataset.keycode; frame.contentWindow?.focus(); doc.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{key:button.dataset.key,code:button.dataset.code,keyCode:n,which:n,bubbles:true,cancelable:true})); button.classList.toggle('held',down)}
// Following the finger once it leaves the control is worth having, but
// it is not worth a lost press: setPointerCapture throws if the pointer
// is already gone, and doing it before the press meant the throw ate
// the input. Press first, then try to follow.
function capture(element,event){
 try{element.setPointerCapture(event.pointerId)}catch(e){}}
document.querySelectorAll('[data-key]:not(#codeload):not([data-pad])').forEach(b=>{b.addEventListener('pointerdown',e=>{e.preventDefault();active.set(e.pointerId,b);key(b,true);capture(b,e)});b.addEventListener('pointerup',e=>{e.preventDefault();if(active.get(e.pointerId)===b){key(b,false);active.delete(e.pointerId)}});b.addEventListener('pointercancel',e=>{if(active.get(e.pointerId)===b){key(b,false);active.delete(e.pointerId)}})});
// A d-pad that behaves like a physical one.
//
// Four separate buttons could only ever press one arrow. A pointer is
// captured by the element it lands on, so a thumb resting between up
// and left sent up alone and Chuck walked straight. Diagonals are
// ordinary movement here -- a keyboard player just holds two arrows --
// so the phone was the only place they were missing.
//
// The fix is the one Microsoft's touch-control guidance gives for a 2D
// game with eight directions: an 8-way d-pad, where "multiple
// directions can be activated together", rather than a joystick. So the
// pad is read as one control instead of four buttons. The touch is
// measured from the pad's centre: inside a small dead zone it means
// nothing, and outside it the angle picks one of eight sectors -- and a
// diagonal simply holds both of its arrows down. Sliding the thumb
// round re-reads the angle, so a direction can be changed without
// lifting off, which is the other thing a physical pad does.
//
// The cardinal sectors are wider than the diagonal ones, 50 degrees
// against 40. Eight equal sectors make a clean diagonal easy and a
// clean "up" hard, and "up" is what a menu wants.
const pad=document.getElementById('pad');
const PAD_SECTORS=[[335,360,['right']],[0,25,['right']],[25,65,['up','right']],
 [65,115,['up']],[115,155,['up','left']],[155,205,['left']],
 [205,245,['down','left']],[245,295,['down']],[295,335,['down','right']]];
const PAD_DEAD=0.22;
const padHeld=new Set(); let padPointer=null;
function padDirections(event){
 const r=pad.getBoundingClientRect();
 const dx=event.clientX-(r.left+r.width/2),dy=event.clientY-(r.top+r.height/2);
 const reach=Math.min(r.width,r.height)/2;
 if(Math.hypot(dx,dy)<reach*PAD_DEAD)return [];
 let a=Math.atan2(-dy,dx)*180/Math.PI; if(a<0)a+=360;
 for(const [from,to,dirs] of PAD_SECTORS){if(a>=from&&a<to)return dirs}
 return [];
}
function padApply(dirs){
 const wanted=new Set(dirs);
 for(const dir of [...padHeld]){if(!wanted.has(dir)){
  key(document.getElementById(dir),false);padHeld.delete(dir)}}
 for(const dir of wanted){if(!padHeld.has(dir)){
  key(document.getElementById(dir),true);padHeld.add(dir)}}
}
function padRelease(){padApply([]);padPointer=null}
pad.addEventListener('pointerdown',e=>{e.preventDefault();padPointer=e.pointerId;
 padApply(padDirections(e));capture(pad,e)});
pad.addEventListener('pointermove',e=>{
 if(e.pointerId!==padPointer)return; e.preventDefault();padApply(padDirections(e))});
for(const kind of ['pointerup','pointercancel']){
 pad.addEventListener(kind,e=>{
  if(e.pointerId===padPointer){e.preventDefault();padRelease()}})}
const root=document.documentElement; document.getElementById('settings').onclick=()=>document.getElementById('panel').classList.add('open');document.getElementById('close').onclick=()=>document.getElementById('panel').classList.remove('open');
// Full screen where the browser has it. Android Chrome does; iPhone
// Safari has no Fullscreen API at all, so the button is removed rather
// than left there doing nothing, and the panel points at Add to Home
// Screen instead, which is the only way to lose the bars on iOS.
const fullscreen=document.getElementById('fullscreen');
const root0=document.documentElement;
const canFullscreen=!!(root0.requestFullscreen||root0.webkitRequestFullscreen);
// Already launched from the home screen: there are no browser bars to
// lose, so the note has nothing to offer.
const installed=matchMedia('(display-mode: standalone)').matches
 ||matchMedia('(display-mode: fullscreen)').matches||navigator.standalone===true;
if(installed)document.getElementById('installnote').hidden=true;
if(!canFullscreen){fullscreen.remove()}
else{document.getElementById('installnote').hidden=true;
 fullscreen.onclick=async()=>{try{
  if(document.fullscreenElement||document.webkitFullscreenElement){
   await (document.exitFullscreen?document.exitFullscreen():document.webkitExitFullscreen())}
  else{await (root0.requestFullscreen?root0.requestFullscreen():root0.webkitRequestFullscreen());
   // Only meaningful once full screen, and refused on desktop; either
   // way a failure here must not lose the full screen we just got.
   try{await screen.orientation.lock('landscape')}catch(e){}}
 }catch(e){}}}
// Control size and inset, kept between visits.
//
// The size slider moves one multiplier and every control follows it:
// the pad, the buttons and the two round chips. It used to widen the
// clamp bounds instead, which on a phone did almost nothing -- the
// floor wins at those viewports -- and never touched the pad at all,
// because the pad sizes itself from its own variable.
//
// Remembering the choice matters more here than on a desktop: these are
// sized to a hand, and re-finding the right size on every visit is the
// kind of small tax that stops people playing.
const sizeInput=document.getElementById('size'),insetInput=document.getElementById('inset');
const SIZE_KEY='chuck.touch.controls';
const applySize=v=>root.style.setProperty('--scale',v/100);
const applyInset=v=>root.style.setProperty('--edge',`clamp(12px,${v/10}vmin,${v}px)`);
try{const saved=JSON.parse(localStorage.getItem(SIZE_KEY)||'null');
 if(saved&&saved.size){sizeInput.value=saved.size;applySize(saved.size)}
 if(saved&&saved.inset!=null){insetInput.value=saved.inset;applyInset(saved.inset)}
}catch(e){/* private mode, blocked storage: the defaults are fine */}
function remember(){try{localStorage.setItem(SIZE_KEY,JSON.stringify(
 {size:+sizeInput.value,inset:+insetInput.value}))}catch(e){}}
sizeInput.oninput=e=>{applySize(e.target.value);remember()};
insetInput.oninput=e=>{applyInset(e.target.value);remember()};
document.addEventListener('visibilitychange',()=>{if(document.hidden){for(const b of active.values())key(b,false);active.clear();padRelease()}});
// Entering a save code on a phone.
//
// The game's LOAD CODE page turns browser paste on when it opens, for
// its own reasons, so the shell watches that same flag and puts a field
// up while it is set. The phone's own keyboard does the typing: there
// is nothing to draw, nothing to hit-test, and SDL never sees a
// keystroke. The finished code goes in through the paste door the page
// is already polling, so the shell never learns what a save code is or
// how long one should be -- the game does all the deciding, and its
// LOAD CODE screen is unchanged on every other host.
const codePanel=document.getElementById('code'),codeField=document.getElementById('codefield'),codeNote=document.getElementById('codenote'),codeLoad=document.getElementById('codeload');
const CODE_NOTE='Type or paste your code, then LOAD. Or HIDE this and dial it in with the d-pad.';
function bridge(){try{return (frame.contentWindow&&frame.contentWindow.CHUCKClipboard)||null}catch(e){return null}}
let codeShown=false,codeDismissed=false;
setInterval(()=>{const link=bridge();const asking=!!(link&&link.isPasteEnabled&&link.isPasteEnabled());
 if(!asking)codeDismissed=false;
 const show=asking&&!codeDismissed;
 if(show===codeShown)return;
 codeShown=show;codePanel.classList.toggle('open',show);
 if(show){codeField.value='';codeNote.textContent=CODE_NOTE}else{codeField.blur()}},200);
document.getElementById('codehide').onclick=()=>{codeDismissed=true;codeShown=false;codeField.blur();codePanel.classList.remove('open')};
document.getElementById('codepaste').onclick=async()=>{try{codeField.value=((await navigator.clipboard.readText())||'').trim();codeField.focus()}catch(e){codeNote.textContent='Paste was refused. Long-press the box and choose Paste.'}};
// Hand the code over, wait for the game to take it, then press Enter.
// The wait is the point: events are read before the paste is polled, so
// an Enter sent in the same breath finds the field still empty.
codeLoad.onclick=async()=>{const link=bridge();if(!link)return;
 const text=codeField.value.trim();
 if(!text){codeNote.textContent='Enter your code first.';return}
 if(!link.offerPaste(text)){codeNote.textContent='The game is not asking for a code.';return}
 codeField.blur();
 for(let i=0;i<80&&link.pastePending();i++)await new Promise(r=>setTimeout(r,25));
 key(codeLoad,true);setTimeout(()=>key(codeLoad,false),40)};
</script></body></html>'''


def stage() -> Path:
    import soundfile as sf

    if not STAGE.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError(f"Staging directory escapes the project: {STAGE}")
    STAGE.mkdir(parents=True, exist_ok=True)
    for name in ("src", "data", "assets"):
        target = STAGE / name
        if target.exists():
            if target.resolve().parent != STAGE.resolve():
                raise ValueError(f"Unsafe staging path: {target}")
            shutil.rmtree(target)
        shutil.copytree(ROOT / name, target,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.wav"))
    shutil.copy2(ROOT / "main.py", STAGE / "main.py")
    total_source = total_web = 0
    for source in sorted((ROOT / "assets" / "audio").rglob("*.wav")):
        target = (STAGE / source.relative_to(ROOT)).with_suffix(".ogg")
        # Bounded writes avoid libsndfile's Windows Vorbis stack overflow
        # on a whole music track, and keep conversion memory constant.
        with sf.SoundFile(source) as original:
            with sf.SoundFile(target, "w", samplerate=original.samplerate,
                              channels=original.channels, format="OGG",
                              subtype="VORBIS") as encoded:
                for samples in original.blocks(blocksize=8192):
                    encoded.write(samples)
        total_source += source.stat().st_size
        total_web += target.stat().st_size
    print(f"Audio: {total_source / 1e6:.1f} MB WAV -> {total_web / 1e6:.1f} MB OGG", flush=True)
    return STAGE


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    directory = stage()
    command = [sys.executable, "-m", "pygbag", "--no_opt", "--title", "CHUCK"]
    command.append("--build")
    subprocess.run([*command, str(directory)], check=True)
    web = directory / "build" / "web"
    finalize_web_artifact(web)
    print(f"Browser files: {web}", flush=True)
    if args.serve:
        subprocess.run([sys.executable, "-m", "http.server", "8000",
                        "--bind", "127.0.0.1", "--directory", str(web)], check=True)


if __name__ == "__main__":
    main()
