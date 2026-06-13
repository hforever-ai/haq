"""
Generate category hero images for Aarambha Haq using Imagen 3 on Vertex AI.
Outputs PNG files to frontend/public/scheme-images/cat-{slug}.png

Run:
    python3 scripts/gen_category_images.py                  # all 15 categories
    python3 scripts/gen_category_images.py --only mahila    # single category
    python3 scripts/gen_category_images.py --dry-run        # print prompts only
"""
import argparse, pathlib, sys, time

PROJECT  = "shrutam-academic"
LOCATION = "us-central1"
MODEL    = "imagen-3.0-generate-001"
OUT_DIR  = pathlib.Path(__file__).parent.parent / "frontend/public/scheme-images"

BASE_STYLE = (
    "vibrant cinematic digital painting, warm rich Indian atmosphere, "
    "ultra detailed expressive faces with genuine big smiles and happiness, "
    "golden hour sun rays, warm saffron and golden yellow tones, lush vivid colors, "
    "bokeh background depth, dramatic warm lighting from behind, glowing aura, "
    "absolutely NO text NO letters NO words NO numbers, "
    "subjects placed in center-right half of frame, left portion lighter sky/background, "
    "award-winning illustration by Sachin Teng style, cinematic 16:9 banner, "
    "photorealistic warmth with painterly quality, hyper-expressive emotions"
)

PROMPTS: dict[str, str] = {
    "mahila":
        "happy smiling Indian village woman in colorful embroidered traditional attire, "
        "arms open in warm welcoming gesture, surrounded by marigold flowers and birds, "
        "vintage Indian folk illustration style inspired by Madhubani art and traditional Indian calendar prints, "
        "bold flat colors, decorative floral border elements, warm saffron yellow and green tones, "
        "joyful celebration mood, NOT photorealistic, painterly illustrated artwork, "
        "stylized expressive face with big warm smile, intricate fabric patterns",

    "student":
        "young Indian university student man smiling confidently holding diploma and books, "
        "graduation cap on head, warm golden campus background, "
        "sunlight streaming through, upward rising stars and sparkles, "
        "academic achievement and bright future, warm saffron and gold tones",

    "farmer":
        "happy Indian farmer couple celebrating harvest, man lifting sheaf of golden wheat triumphantly, "
        "woman laughing brightly in green saree, surrounded by lush golden crops, "
        "warm setting sun painting everything gold and orange, "
        "prosperous abundant harvest, tractor in background, pure joy on their faces",

    "employment":
        "confident young Indian man and woman with bright happy smiles, "
        "one holding laptop one holding tools, thumbs up gesture, "
        "city skyline and rising sun behind them, upward arrow motif, "
        "dynamic energy, modern professional, success and opportunity vibe",

    "disability":
        "person in wheelchair with arms outstretched toward bright sun, "
        "supportive community hands around them, accessibility ramp and stars, "
        "soft purple and gold accent tones, inclusive and uplifting",

    "pension":
        "happy elderly Indian grandparents sitting under a banyan tree, "
        "small grandchild beside them, coins and folded document nearby, "
        "warm sunset orange glow, peaceful contentment",

    "health":
        "Indian family with a caring doctor holding stethoscope, "
        "red cross and green leaf motifs, clean hospital setting in background, "
        "protective hands over family silhouette, soft caring atmosphere",

    "child":
        "Indian children playing with colorful kites against blue sky, "
        "open books and crayons scattered, bright rainbow colors, "
        "joyful running poses, balloons and butterflies",

    "tribal":
        "tribal Indian community in vibrant traditional attire, "
        "forest trees and tribal geometric patterns as border, "
        "peacock and mountain motifs, rich greens and earth tones, "
        "cultural pride and dignity",

    "bpl":
        "Indian family of four standing in front of newly built pucca house, "
        "sunrise breaking behind the house, construction worker motif, "
        "hopeful expressions, rising sun rays in saffron and gold",

    "housing":
        "smiling Indian family holding keys to new home, "
        "small house with Indian flag colors, tree and garden beside it, "
        "golden sunrise, sense of security and belonging",

    "entrepreneur":
        "young Indian woman running a small business, bright shop front with goods, "
        "money plant growing from open hands, digital tablet and coins, "
        "startup energy, green growth motifs",

    "minority":
        "diverse group of Indian people from different communities together, "
        "multiple cultural symbols (crescent, diya, cross) united, "
        "hands joined in circle motif, rainbow arc, harmony and inclusion",

    "maternity":
        "gentle Indian mother cradling newborn, soft pink and gold palette, "
        "lotus cradle, nurturing warmth, healthcare worker silhouette nearby, "
        "stars and soft light rays, tender protective atmosphere",

    "elderly":
        "dignified elderly Indian man smiling, receiving folded document, "
        "walking stick beside him, loving family silhouette in background, "
        "golden hour light, sense of security and respect",
}


def generate(slug: str, prompt: str, dry_run: bool, force: bool = False) -> bool:
    full_prompt = f"{prompt}, {BASE_STYLE}"
    out_path = OUT_DIR / f"cat-{slug}.png"

    if dry_run:
        print(f"\n── {slug} ──")
        print(full_prompt[:200] + "...")
        return True

    if out_path.exists() and not force:
        print(f"  skip {slug} (exists, use --force to regenerate)")
        return True

    try:
        from google import genai as gai
        from google.genai import types as gtypes
        gclient = gai.Client(vertexai=True, project=PROJECT, location=LOCATION)
        resp = gclient.models.generate_images(
            model=MODEL,
            prompt=full_prompt,
            config=gtypes.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                person_generation="ALLOW_ADULT",
            )
        )
        img_bytes = resp.generated_images[0].image.image_bytes
        out_path.write_bytes(img_bytes)
        print(f"  ✓ {slug} → {out_path.name}")
        return True

    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            print(f"  ⏳ {slug}: quota hit, retrying in 60s...", file=sys.stderr)
            time.sleep(60)
            return generate(slug, prompt, dry_run, force)   # one retry
        print(f"  ✗ {slug}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Comma-separated category slugs to generate, e.g. mahila,farmer")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts, don't call API")
    parser.add_argument("--force", action="store_true", help="Overwrite existing images")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.only:
        slugs = [s.strip() for s in args.only.split(",")]
    else:
        slugs = list(PROMPTS.keys())
    ok = err = 0

    for slug in slugs:
        if slug not in PROMPTS:
            print(f"Unknown slug: {slug}. Valid: {list(PROMPTS.keys())}")
            sys.exit(1)
        success = generate(slug, PROMPTS[slug], args.dry_run, force=args.force)
        if success:
            ok += 1
        else:
            err += 1
        if not args.dry_run and len(slugs) > 1:
            time.sleep(12)  # ~5 req/min safe rate

    print(f"\nDone: {ok} ok, {err} failed")


if __name__ == "__main__":
    main()
