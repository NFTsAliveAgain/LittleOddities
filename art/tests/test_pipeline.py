"""Automated checks for the art pipeline:  python -m unittest discover -s tests"""
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from oddities import layered  # noqa: E402
from oddities.metadata import token_metadata  # noqa: E402
from oddities.planner import load_config, plan_collection, statistics, verify_plan  # noqa: E402

CFG = load_config()


class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokens = plan_collection(CFG)

    def test_exact_rarity_and_supply(self):
        s = statistics(self.tokens, CFG)
        self.assertEqual(s["tiers"], {"Common": 5000, "Uncommon": 3000, "Rare": 1500, "Epic": 400, "Legendary": 100})
        self.assertEqual([t["id"] for t in self.tokens], list(range(1, 10001)))

    def test_all_guarantees(self):
        self.assertEqual(verify_plan(self.tokens, CFG), [])

    def test_reproducible(self):
        again = plan_collection(CFG)
        self.assertEqual([t["dna"] for t in again[:200]], [t["dna"] for t in self.tokens[:200]])

    def test_metadata_shape(self):
        m = token_metadata(self.tokens[0], CFG)
        self.assertEqual(m["image"], "ipfs://__IMAGES_CID__/1.png")
        self.assertEqual(m["attributes"][0]["trait_type"], "Rarity")
        self.assertEqual(len(m["attributes"]), 1 + len(CFG["categories"]))


class LayerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = layered.LAYERS
        layered.LAYERS = Path(self.tmp.name)
        layered._load.cache_clear()

    def tearDown(self):
        layered.LAYERS = self.old
        layered._load.cache_clear()
        self.tmp.cleanup()

    def _write(self, key, name, draw):
        p = layered.layer_path(key, name)
        p.parent.mkdir(parents=True, exist_ok=True)
        im = Image.new("RGBA", (2048, 2048), (0, 0, 0, 0))
        draw(ImageDraw.Draw(im))
        im.save(p)

    def test_full_render_with_tint_and_clip(self):
        traits = {"background": "Forest", "species": "Cat", "color": "Blue", "pattern": "Spots", "eyes": "Normal",
                  "mouth": "Smile", "clothing": "None", "accessory": "None", "headwear": "None", "special": "None"}
        self._write("background", "Forest", lambda d: d.rectangle([0, 0, 2048, 2048], fill=(40, 160, 60, 255)))
        self._write("species", "Cat.fill", lambda d: d.ellipse([524, 524, 1524, 1524], fill=(255, 255, 255, 255)))
        self._write("species", "Cat", lambda d: d.ellipse([524, 524, 1524, 1524], outline=(0, 0, 0, 255), width=20))
        # pattern drawn partly OUTSIDE the body: must be clipped away
        self._write("pattern", "Spots", lambda d: d.rectangle([0, 1000, 2048, 1100], fill=(255, 0, 0, 255)))
        self._write("eyes", "Normal", lambda d: d.ellipse([900, 900, 950, 950], fill=(0, 0, 0, 255)))
        self._write("mouth", "Smile", lambda d: d.line([900, 1200, 1100, 1200], fill=(0, 0, 0, 255), width=10))
        img, qa = layered.render_layered(traits, CFG, out_size=1024)
        self.assertTrue(qa["ok"], qa)
        self.assertEqual(img.getpixel((50, 50)), (40, 160, 60))          # background
        self.assertEqual(img.getpixel((50, 525)), (40, 160, 60))         # pattern clipped outside body
        r, g, b = img.getpixel((512, 400))                               # body tinted blue (#5BA8F5)
        self.assertTrue(b > r and abs(b - 0xF5) < 6, (r, g, b))
        self.assertEqual(img.getpixel((512, 525))[:1], (255,))           # pattern visible inside body

    def test_missing_layers_give_placeholder(self):
        t = plan_collection(CFG)[0]["traits"]
        img, qa = layered.render_layered(t, CFG, out_size=512)
        self.assertTrue(qa["placeholder"])
        self.assertFalse(qa["ok"])


if __name__ == "__main__":
    unittest.main()
