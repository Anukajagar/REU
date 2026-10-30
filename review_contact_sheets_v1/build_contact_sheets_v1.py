r"""Build review-only contact sheets from the ICA sign-off packet (v2 review ZIP).

Reads (never writes) the component maps and manifest inside
`EEG processed\quality_control\ica_signoff_packet_v2_review.zip`, cross-checks the
bundled PNGs against the frozen originals in `EEG processed\eeg\figures_v2\ica\`,
and renders two contact-sheet PNGs plus a label CSV.

No verdict, disposition or sign-off state is assigned, inferred or written anywhere.
"""

from __future__ import annotations

import csv
import hashlib
import io
import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

ROOT = r"E:\REU_DATA"
PACK = os.path.join(ROOT, "EEG processed", "quality_control", "ica_signoff_packet_v2_review.zip")
FROZEN_DIR = os.path.join(ROOT, "EEG processed", "eeg", "figures_v2", "ica")
OUT_DIR = os.path.join(ROOT, "review_contact_sheets_v1")

SHEET_ALL = os.path.join(OUT_DIR, "contact_sheet_ica_maps_all30_v1.png")
SHEET_NEAR = os.path.join(OUT_DIR, "contact_sheet_near_guard_3_v1.png")
LABELS_CSV = os.path.join(OUT_DIR, "contact_sheet_labels_all30_v1.csv")

NEAR_GUARD = ["P02_calm", "P06_maths", "P09_maths"]  # as requested
CONDITION_ORDER = {"calm": 0, "maths": 1, "meditation": 2}

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG = r"C:\Windows\Fonts\arial.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def load_rgba(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    img.load()
    bg = Image.new("RGB", img.size, "white")
    bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
    return bg


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def thumb(img: Image.Image, width: int) -> Image.Image:
    height = round(img.height * width / img.width)
    return img.resize((width, height), Image.LANCZOS)


def draw_sheet(
    path: str,
    title: str,
    subtitle: str,
    footer: list[str],
    tiles: list[dict],
    cols: int,
    thumb_w: int,
    label_h: int,
    header_h: int,
    font_label: ImageFont.FreeTypeFont,
    font_small: ImageFont.FreeTypeFont,
    font_title: ImageFont.FreeTypeFont,
    font_sub: ImageFont.FreeTypeFont,
) -> None:
    margin, gap, pad = 40, 20, 12
    rows = -(-len(tiles) // cols)
    cell_w = thumb_w
    sheet_w = margin * 2 + cols * cell_w + (cols - 1) * gap
    first_thumb_h = thumb(Image.open(io.BytesIO(tiles[0]["bytes"])).convert("RGB"), thumb_w).height
    cell_h = first_thumb_h + label_h
    sheet_h = header_h + rows * cell_h + (rows - 1) * gap + margin * 2 + len(footer) * 30

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    d = ImageDraw.Draw(sheet)

    d.text((margin, 28), title, font=font_title, fill="black")
    d.text((margin, 78), subtitle, font=font_sub, fill=(60, 60, 60))

    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        x = margin + c * (cell_w + gap)
        y = header_h + r * (cell_h + gap)
        im = thumb(Image.open(io.BytesIO(t["bytes"])).convert("RGB"), thumb_w)
        sheet.paste(im, (x, y))
        d.rectangle([x - 1, y - 1, x + im.width, y + im.height], outline=(170, 170, 170))
        ly = y + im.height + pad
        d.text((x, ly), t["line1"], font=font_label, fill="black")
        d.text((x, ly + 34), t["line2"], font=font_small, fill=(40, 40, 40))

    fy = sheet_h - margin - len(footer) * 30
    for i, line in enumerate(footer):
        d.text((margin, fy + i * 30), line, font=font_small, fill=(90, 90, 90))

    sheet.save(path, "PNG")
    print(f"wrote {path}  ({sheet.width}x{sheet.height}, {len(tiles)} tiles)")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    z = zipfile.ZipFile(PACK)

    with io.TextIOWrapper(z.open("packet_manifest_v2.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 30, f"expected 30 manifest rows, got {len(rows)}"

    entries: dict[str, str] = {
        os.path.basename(n): n for n in z.namelist() if n.startswith("component_maps/") and n.endswith(".png")
    }
    assert len(entries) == 30, f"expected 30 component maps in ZIP, got {len(entries)}"

    tiles: list[dict] = []
    for row in rows:
        pid, cond = row["participant"], row["condition"]
        name = f"{pid}_{cond}_components.png"
        assert name in entries, f"missing component map for {pid} {cond}"
        data = z.read(entries[name])

        frozen = os.path.join(FROZEN_DIR, name)
        with open(frozen, "rb") as fh:
            frozen_bytes = fh.read()
        assert sha256(data) == sha256(frozen_bytes), f"bundled map differs from frozen original: {name}"

        tiles.append(
            {
                "participant": pid,
                "condition": cond,
                "components_removed": row["components_removed"],
                "entry": entries[name],
                "bytes": data,
                "sha256": sha256(data),
                "line1": f"{pid}  |  {cond}",
                "line2": f"removed components: {row['components_removed']}",
            }
        )

    tiles.sort(key=lambda t: (t["participant"], CONDITION_ORDER.get(t["condition"], 99)))
    assert len({f"{t['participant']}_{t['condition']}" for t in tiles}) == 30

    footer = [
        "Sources: EEG processed\\quality_control\\ica_signoff_packet_v2_review.zip "
        "(component_maps/ + packet_manifest_v2.csv), cross-checked byte-for-byte against "
        "EEG processed\\eeg\\figures_v2\\ica\\ (read-only).",
        "Review aid only. Labels reproduce the manifest values verbatim. "
        "No verdict, disposition or sign-off decision is assigned by this sheet.",
    ]

    draw_sheet(
        SHEET_ALL,
        "ICA component maps - review contact sheet (all 30 recordings)",
        "Participant ID  |  condition  |  removed component indices   -   review only, no verdicts assigned",
        footer,
        tiles,
        cols=5,
        thumb_w=440,
        label_h=86,
        header_h=150,
        font_label=font(FONT_BOLD, 26),
        font_small=font(FONT_REG, 18),
        font_title=font(FONT_BOLD, 36),
        font_sub=font(FONT_REG, 22),
    )

    near = [t for t in tiles if f"{t['participant']}_{t['condition']}" in NEAR_GUARD]
    order = {k: i for i, k in enumerate(NEAR_GUARD)}
    near.sort(key=lambda t: order[f"{t['participant']}_{t['condition']}"])
    assert len(near) == 3, f"expected 3 near-guard recordings, got {len(near)}"

    flagged = sorted(
        f"{r['participant']}_{r['condition']}" for r in rows if r["near_guard_flag"].strip().upper() == "YES"
    )
    assert flagged == sorted(NEAR_GUARD), f"manifest near-guard set {flagged} != requested {sorted(NEAR_GUARD)}"

    draw_sheet(
        SHEET_NEAR,
        "Near-guard ICA component maps - review contact sheet (3 recordings)",
        "P02 calm  |  P06 maths  |  P09 maths   -   review only, no verdicts assigned",
        footer,
        near,
        cols=3,
        thumb_w=640,
        label_h=96,
        header_h=150,
        font_label=font(FONT_BOLD, 30),
        font_small=font(FONT_REG, 20),
        font_title=font(FONT_BOLD, 36),
        font_sub=font(FONT_REG, 22),
    )

    with open(LABELS_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "sheet",
                "tile_index",
                "participant",
                "condition",
                "recording",
                "components_removed",
                "source_zip",
                "source_entry",
                "source_sha256",
                "frozen_original_path",
            ]
        )
        for sheet_name, subset in (
            ("contact_sheet_ica_maps_all30_v1.png", tiles),
            ("contact_sheet_near_guard_3_v1.png", near),
        ):
            for i, t in enumerate(subset, start=1):
                w.writerow(
                    [
                        sheet_name,
                        i,
                        t["participant"],
                        t["condition"],
                        f"{t['participant']}_{t['condition']}",
                        t["components_removed"],
                        PACK,
                        t["entry"],
                        t["sha256"],
                        os.path.join(FROZEN_DIR, f"{t['participant']}_{t['condition']}_components.png"),
                    ]
                )
    print(f"wrote {LABELS_CSV}")

    print("checks: 30/30 manifest rows, 30/30 bundled maps, 30/30 byte-identical to frozen originals, "
          "3/3 near-guard labels match manifest near_guard_flag=YES")


if __name__ == "__main__":
    main()
