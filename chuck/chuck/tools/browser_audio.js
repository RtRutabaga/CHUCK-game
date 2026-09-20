// Play like a music or video app, not like a notification.
//
// iOS mutes Web Audio when the ring/silent switch is on, which is why a
// phone with the switch flipped hears nothing while the same build is
// audible on a PC and on the Xbox. It is not a bug in the mixer: the
// system is doing what the switch asks, because by default the browser
// files a page's audio under "ambient" -- incidental sound that should
// respect silent mode.
//
// Safari 16.4 added the AudioSession API to say otherwise. Declaring
// the type "playback" means this is the main content, the thing the
// player came for, exactly as a music or video app declares it -- and
// the silent switch stops applying.
//
// The trade it makes, which is the right one for a game: playback audio
// interrupts other apps' audio rather than mixing under it, and stops
// when the page goes to the background.
//
// Everywhere else this is simply absent and nothing happens.
(() => {
  try {
    if (navigator.audioSession) {
      navigator.audioSession.type = "playback";
    }
  } catch (error) {
    // A browser that has the property but refuses the value is not
    // worth a crash; the game is still playable with the switch off.
  }
})();
