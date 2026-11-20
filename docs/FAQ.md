# FAQ

**Does this work with every game?** No. It works best where text is in readable files or well-known containers. See the support table in the README for honest status per engine.

**Will I get banned?** Modifying files of games with online anti-cheat can lead to bans. Use GameLingo for offline/single-player games only.

**Can I share my translation?** Share only your overlay (translated text and fonts you may redistribute), never the game's files. Check the publisher's policy. See `skills/gamelingo/references/legal-and-safety.md`.

**Is the translation good?** Claude translates with context and a glossary, but machine translation needs review. Use the QA skill, play-test, and let native speakers proofread.

**Why does Arabic look broken in some games?** Engines differ in shaping, bidi and fonts. See `skills/gamelingo/references/rtl-arabic.md`.

**What happens after a game update?** Updates (and "Verify integrity") overwrite patched files. Re-apply the overlay.

**Do I need to know Python?** No; Claude runs the scripts. Python 3.9+ must be installed.
