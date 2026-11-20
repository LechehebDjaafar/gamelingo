import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "gamelingo" / "scripts"
DEMO = ROOT / "examples" / "demo-game"
sys.path.insert(0, str(SCRIPTS))

import placeholders  # noqa: E402
import qa_check  # noqa: E402
import rtl  # noqa: E402
import strings_io  # noqa: E402
import detect_engine  # noqa: E402


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True)


class PlaceholderTests(unittest.TestCase):
    def test_find_common_tokens(self):
        toks = placeholders.find_tokens(r"\N[1]: Hi {player}, %d <b>gold</b> %1$s \n \C[2]x")
        self.assertEqual(sorted(toks), sorted([r"\N[1]", "{player}", "%d", "<b>", "</b>", "%1$s", r"\n", r"\C[2]"]))

    def test_percent_sign_in_prose_is_not_a_token(self):
        self.assertEqual(placeholders.find_tokens("100% sure about 50 % of it"), [])

    def test_protect_restore_roundtrip(self):
        src = r"\C[2]Hello\C[0] {name}, you have %d items"
        masked, tokens = placeholders.protect(src)
        self.assertNotIn("{name}", masked)
        self.assertEqual(placeholders.restore(masked, tokens), src)

    def test_restore_tolerates_spaces(self):
        masked, tokens = placeholders.protect("Hi {name}")
        self.assertEqual(placeholders.restore(masked.replace("⟦0⟧", "⟦ 0 ⟧"), tokens), "Hi {name}")


class StringsIOTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)

    def extract(self, *args):
        table = self.out / "t.jsonl"
        r = run("strings_io.py", "extract", *args, "-o", table)
        self.assertEqual(r.returncode, 0, r.stderr)
        return [json.loads(l) for l in table.read_text(encoding="utf-8").splitlines()]

    def test_json_extract_with_key_filter(self):
        rows = self.extract(DEMO / "data" / "Actors.json", "--keys", "name,profile")
        sources = [r["source"] for r in rows]
        self.assertIn("Lyra", sources)
        self.assertTrue(any("parcels" in s for s in sources))
        self.assertNotIn("Actor1", sources)

    def test_json_roundtrip_preserves_structure_and_minification(self):
        src = DEMO / "data" / "Actors.json"
        rows = self.extract(src, "--keys", "name")
        for r in rows:
            r["target"] = "ع-" + r["source"]
        table = self.out / "t.jsonl"
        table.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
        dest = self.out / "overlay"
        r = run("strings_io.py", "apply", src, table, "-o", dest)
        self.assertEqual(r.returncode, 0, r.stderr)
        new = json.loads((dest / "Actors.json").read_text(encoding="utf-8"))
        self.assertEqual(new[1]["name"], "ع-Lyra")
        self.assertEqual(new[1]["faceName"], "Actor1")
        self.assertIsNone(new[0])
        self.assertEqual((dest / "Actors.json").read_text(encoding="utf-8").strip().count("\n"), 0)

    def test_nested_event_commands_are_reachable(self):
        rows = self.extract(DEMO / "data" / "Map001.json", "--keys", "parameters", "--min-len", "5")
        self.assertTrue(any("bridge is out" in r["source"] for r in rows))

    def test_refuses_to_overwrite_source(self):
        src = DEMO / "data" / "Actors.json"
        table = self.out / "t.jsonl"
        table.write_text(json.dumps({"id": "/1/name", "file": "Actors.json", "source": "Lyra", "target": "X"}))
        r = run("strings_io.py", "apply", src, table, "-o", src)
        self.assertEqual(r.returncode, 2)

    def test_csv_roundtrip_adds_target_column(self):
        src = DEMO / "locale" / "strings.csv"
        rows = self.extract(src, "--source-col", "en")
        self.assertEqual(len(rows), 4)
        self.assertIn("Welcome, {player}!\nYour journey begins.", [r["source"] for r in rows])
        for r in rows:
            r["target"] = "AR:" + r["source"]
        table = self.out / "t.jsonl"
        table.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
        dest = self.out / "o"
        r = run("strings_io.py", "apply", src, table, "-o", dest, "--target-col", "ar")
        self.assertEqual(r.returncode, 0, r.stderr)
        import csv
        with open(dest / "strings.csv", encoding="utf-8", newline="") as fh:
            got = list(csv.reader(fh))
        self.assertEqual(got[0], ["key", "en", "fr", "ar"])
        self.assertEqual(got[1][3], "AR:Start Game")
        self.assertEqual(got[4][3], "AR:Welcome, {player}!\nYour journey begins.")

    def test_po_extract_handles_context_multiline_and_plurals(self):
        rows = self.extract(DEMO / "locale" / "game.po")
        ids = [r["id"] for r in rows]
        self.assertIn("Continue", ids)
        self.assertIn("menu\x04Options", ids)
        self.assertIn("You found %d coins and a very long description that continues on the next line.", ids)
        self.assertNotIn("Item", ids)  # plural entries are skipped

    def test_po_roundtrip(self):
        src = DEMO / "locale" / "game.po"
        rows = self.extract(src)
        for r in rows:
            r["target"] = "ترجمة " + r["source"].split("\n")[0]
        table = self.out / "t.jsonl"
        table.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
        dest = self.out / "o"
        self.assertEqual(run("strings_io.py", "apply", src, table, "-o", dest).returncode, 0)
        out = (dest / "game.po").read_text(encoding="utf-8")
        self.assertIn('msgstr "ترجمة Continue"', out)
        self.assertIn('msgstr[0] ""', out)  # plural untouched
        again = strings_io.parse_po(out.splitlines())
        self.assertEqual(sum(1 for e in again if e.get("msgstr", "").startswith("ترجمة")), 3)

    def test_properties_roundtrip(self):
        src = DEMO / "locale" / "en.properties"
        rows = self.extract(src)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[2]["source"], "Press Space to jump.\nHold to jump higher.")
        rows[0]["target"] = "العب"
        table = self.out / "t.jsonl"
        table.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
        dest = self.out / "o"
        self.assertEqual(run("strings_io.py", "apply", src, table, "-o", dest).returncode, 0)
        out = (dest / "en.properties").read_text(encoding="utf-8")
        self.assertIn("menu.play=العب", out)
        self.assertIn("menu.settings=Settings", out)
        self.assertIn("# demo properties file", out)


class QATests(unittest.TestCase):
    def rows(self, src, tgt):
        return [{"id": "1", "file": "f", "source": src, "target": tgt}]

    def test_placeholder_mismatch_is_error(self):
        rep = qa_check.check(self.rows("Hi {name}, %d", "مرحبا %d"))
        self.assertEqual(rep["errors"], 1)

    def test_clean_translation_passes(self):
        rep = qa_check.check(self.rows("Hi {name}", "مرحبا {name}"), expect_script="arabic")
        self.assertEqual((rep["errors"], rep["warnings"]), (0, 0))

    def test_glossary_miss(self):
        rep = qa_check.check(self.rows("Go to the Moonlit Valley", "اذهب إلى الوادي"),
                             glossary={"Moonlit Valley": "وادي القمر"})
        self.assertEqual(rep["warnings"], 1)

    def test_wrong_script_and_length(self):
        rep = qa_check.check(self.rows("Open the ancient door slowly", "Ouvrir la porte ancienne lentement"),
                             expect_script="arabic")
        self.assertTrue(any(i["code"] == "script" for i in rep["issues"]))

    def test_untranslated_counted(self):
        rep = qa_check.check(self.rows("Hello there", ""))
        self.assertEqual(rep["untranslated"], 1)


@unittest.skipUnless(all(rtl._libs()), "arabic-reshaper / python-bidi not installed")
class RTLTests(unittest.TestCase):
    def test_shape_converts_to_presentation_forms(self):
        out = rtl.process("مرحبا", "shape")
        self.assertTrue(any("\uFE70" <= c <= "\uFEFF" for c in out))

    def test_visual_reverses_order(self):
        shaped = rtl.process("بسم", "shape")
        self.assertEqual(rtl.process("بسم", "visual"), shaped[::-1])

    def test_latin_untouched_and_none_mode(self):
        self.assertEqual(rtl.process("Hello", "visual"), "Hello")
        self.assertEqual(rtl.process("مرحبا", "none"), "مرحبا")

    def test_only_rtl_lines_are_processed(self):
        out = rtl.process("Line one\nمرحبا", "shape")
        self.assertTrue(out.startswith("Line one\n"))


class DetectTests(unittest.TestCase):
    def test_demo_game_detected_as_rpg_maker(self):
        res = detect_engine.detect(DEMO)
        self.assertEqual(res["engines"][0]["engine"], "RPG Maker MV/MZ")
        self.assertTrue(any(c["path"].endswith("strings.csv") for c in res["text_candidates"]))

    def test_unity_il2cpp_detection(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "Game_Data").mkdir()
            (root / "Game_Data" / "globalgamemanagers").write_bytes(b"x")
            (root / "UnityPlayer.dll").write_bytes(b"x")
            (root / "GameAssembly.dll").write_bytes(b"x")
            res = detect_engine.detect(root)
            self.assertEqual(res["engines"][0]["engine"], "Unity")
            self.assertEqual(res["engines"][0]["variant"], "IL2CPP")

    def test_unreal_detection(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "Engine").mkdir()
            (root / "Game" / "Content" / "Paks").mkdir(parents=True)
            (root / "Game" / "Content" / "Paks" / "game-WindowsNoEditor.pak").write_bytes(b"x")
            (root / "Game" / "Content" / "Localization").mkdir()
            (root / "Game" / "Content" / "Localization" / "Game.locres").write_bytes(b"x")
            res = detect_engine.detect(root)
            self.assertEqual(res["engines"][0]["engine"], "Unreal Engine")


class BackupTests(unittest.TestCase):
    def test_snapshot_modify_restore(self):
        with tempfile.TemporaryDirectory() as t:
            game, bk = Path(t) / "game", Path(t) / "bk"
            (game / "data").mkdir(parents=True)
            f = game / "data" / "a.json"
            f.write_text("original", encoding="utf-8")
            r = run("backup.py", "snapshot", game, bk, "--paths", "data/a.json", "data/new_font.ttf")
            self.assertEqual(r.returncode, 0, r.stderr)
            f.write_text("MODIFIED", encoding="utf-8")
            (game / "data" / "new_font.ttf").write_bytes(b"font")
            self.assertEqual(run("backup.py", "verify", bk).returncode, 0)
            r = run("backup.py", "restore", bk)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(f.read_text(encoding="utf-8"), "original")
            self.assertFalse((game / "data" / "new_font.ttf").exists())

    def test_rejects_path_traversal_and_overwriting_backup(self):
        with tempfile.TemporaryDirectory() as t:
            game, bk = Path(t) / "g", Path(t) / "bk"
            game.mkdir()
            self.assertNotEqual(run("backup.py", "snapshot", game, bk, "--paths", "../evil").returncode, 0)
            self.assertEqual(run("backup.py", "snapshot", game, bk, "--paths", "x").returncode, 0)
            self.assertNotEqual(run("backup.py", "snapshot", game, bk, "--paths", "x").returncode, 0)

    def test_corrupt_backup_blocks_restore(self):
        with tempfile.TemporaryDirectory() as t:
            game, bk = Path(t) / "g", Path(t) / "bk"
            game.mkdir()
            (game / "a.txt").write_text("hello")
            run("backup.py", "snapshot", game, bk, "--paths", "a.txt")
            (bk / "files" / "a.txt").write_text("tampered")
            self.assertNotEqual(run("backup.py", "restore", bk).returncode, 0)


if __name__ == "__main__":
    unittest.main()
