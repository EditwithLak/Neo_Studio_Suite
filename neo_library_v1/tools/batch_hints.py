import argparse
from pathlib import Path

from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageOps, ImageFilter
from tqdm import tqdm

# OK Import detectors directly (avoids controlnet_aux/__init__.py -> mediapipe crash)
from controlnet_aux.canny import CannyDetector
from controlnet_aux.open_pose import OpenposeDetector
from controlnet_aux.midas import MidasDetector

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _hex_to_rgb(s: str, fallback=(255, 255, 255)):
    try:
        s = (s or "").strip().lstrip("#")
        if len(s) == 3:
            s = "".join([c + c for c in s])
        if len(s) != 6:
            return fallback
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        return (r, g, b)
    except Exception:
        return fallback


def _pick_anchor_xy(base_w: int, base_h: int, obj_w: int, obj_h: int, pos: str, offx: int, offy: int):
    pos = (pos or "bottom-right").lower()
    offx = int(offx or 0)
    offy = int(offy or 0)

    if pos == "top-left":
        x, y = 0, 0
    elif pos == "top-right":
        x, y = base_w - obj_w, 0
    elif pos == "bottom-left":
        x, y = 0, base_h - obj_h
    elif pos == "bottom-right":
        x, y = base_w - obj_w, base_h - obj_h
    elif pos == "top-center":
        x, y = (base_w - obj_w) // 2, 0
    elif pos == "bottom-center":
        x, y = (base_w - obj_w) // 2, base_h - obj_h
    else:  # center
        x, y = (base_w - obj_w) // 2, (base_h - obj_h) // 2

    x += offx
    y += offy
    return int(x), int(y)


def _load_font(size: int):
    size = int(_clamp(int(size or 28), 6, 512))
    # Try common fonts (Windows + fallback). If none, PIL default.
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "arial.ttf",
        "DejaVuSans.ttf",
    ]
    for fp in candidates:
        try:
            return ImageFont.truetype(fp, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def apply_overlay_png(
    base_rgb: Image.Image,
    overlay_path: str,
    pos: str,
    scale: float,
    opacity: float,
    offx: int,
    offy: int,
) -> Image.Image:
    if not overlay_path:
        return base_rgb
    p = Path(overlay_path)
    if not p.exists():
        return base_rgb

    base = base_rgb.convert("RGBA")
    ow, oh = base.size

    try:
        ov = Image.open(p).convert("RGBA")
    except Exception:
        return base_rgb

    # scale is % of base width by default
    try:
        s = float(scale)
    except Exception:
        s = 0.25
    s = _clamp(s, 0.01, 2.0)

    target_w = max(1, int(round(ow * s)))
    ratio = target_w / max(1, ov.size[0])
    target_h = max(1, int(round(ov.size[1] * ratio)))
    ov = ov.resize((target_w, target_h), Image.LANCZOS)

    # opacity
    try:
        op = float(opacity)
    except Exception:
        op = 1.0
    op = _clamp(op, 0.0, 1.0)
    if op < 1.0:
        alpha = ov.getchannel("A")
        alpha = alpha.point(lambda a: int(a * op))
        ov.putalpha(alpha)

    x, y = _pick_anchor_xy(ow, oh, ov.size[0], ov.size[1], pos, offx, offy)
    base.alpha_composite(ov, (x, y))
    return base.convert("RGB")


def apply_overlay_text(
    base_rgb: Image.Image,
    text: str,
    size: int,
    color: str,
    outline: bool,
    outline_color: str,
    pos: str,
    offx: int,
    offy: int,
) -> Image.Image:
    text = (text or "").strip()
    if not text:
        return base_rgb

    base = base_rgb.convert("RGBA")
    w, h = base.size
    draw = ImageDraw.Draw(base)
    font = _load_font(size)

    fill = _hex_to_rgb(color, (255, 255, 255))
    ocol = _hex_to_rgb(outline_color, (0, 0, 0))

    # text bbox
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except Exception:
        tw, th = draw.textsize(text, font=font)

    x, y = _pick_anchor_xy(w, h, tw, th, pos, offx, offy)

    if outline:
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
            draw.text((x + dx, y + dy), text, font=font, fill=ocol)
    draw.text((x, y), text, font=font, fill=fill)
    return base.convert("RGB")


def apply_overlays(prepped_rgb: Image.Image, args) -> Image.Image:
    img = prepped_rgb
    if getattr(args, "overlay_png", ""):
        img = apply_overlay_png(
            img,
            overlay_path=getattr(args, "overlay_png", ""),
            pos=getattr(args, "overlay_png_pos", "bottom-right"),
            scale=float(getattr(args, "overlay_png_scale", 0.25) or 0.25),
            opacity=float(getattr(args, "overlay_png_opacity", 1.0) or 1.0),
            offx=int(getattr(args, "overlay_png_offx", 0) or 0),
            offy=int(getattr(args, "overlay_png_offy", 0) or 0),
        )

    if getattr(args, "overlay_text", ""):
        img = apply_overlay_text(
            img,
            text=getattr(args, "overlay_text", ""),
            size=int(getattr(args, "overlay_text_size", 28) or 28),
            color=getattr(args, "overlay_text_color", "#FFFFFF"),
            outline=bool(getattr(args, "overlay_text_outline", False)),
            outline_color=getattr(args, "overlay_text_outline_color", "#000000"),
            pos=getattr(args, "overlay_text_pos", "bottom-right"),
            offx=int(getattr(args, "overlay_text_offx", 0) or 0),
            offy=int(getattr(args, "overlay_text_offy", 0) or 0),
        )
    return img


def parse_size(s: str) -> tuple[int, int]:
    s = s.lower().replace(" ", "")
    if "x" not in s:
        raise ValueError("Size must look like 896x1344")
    w, h = s.split("x", 1)
    return int(w), int(h)


def fit_image(img: Image.Image, target_w: int, target_h: int, mode: str) -> Image.Image:
    """
    mode:
      - 'cover'   => fill target, crop overflow
      - 'contain' => fit inside, pad with black bars
    """
    img = img.convert("RGB")
    in_w, in_h = img.size
    target_ar = target_w / target_h
    in_ar = in_w / in_h

    if mode == "cover":
        scale = (target_h / in_h) if in_ar > target_ar else (target_w / in_w)
        new_w = int(round(in_w * scale))
        new_h = int(round(in_h * scale))
        resized = img.resize((new_w, new_h), Image.BICUBIC)

        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return resized.crop((left, top, left + target_w, top + target_h))

    if mode == "contain":
        scale = (target_w / in_w) if in_ar > target_ar else (target_h / in_h)
        new_w = int(round(in_w * scale))
        new_h = int(round(in_h * scale))
        resized = img.resize((new_w, new_h), Image.BICUBIC)

        canvas = Image.new("RGB", (target_w, target_h), (0, 0, 0))
        left = (target_w - new_w) // 2
        top = (target_h - new_h) // 2
        canvas.paste(resized, (left, top))
        return canvas

    raise ValueError("mode must be 'cover' or 'contain'")


def iter_images(in_dir: Path, recursive: bool):
    if recursive:
        for p in in_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in IMG_EXTS:
                yield p
    else:
        for p in in_dir.iterdir():
            if p.is_file() and p.suffix.lower() in IMG_EXTS:
                yield p


def apply_optional_blur(pil_img: Image.Image, blur_ksize: int) -> Image.Image:
    """
    Small blur before Canny reduces random junk lines.
    blur_ksize must be odd (3,5,7...) or 0 to disable.
    """
    if not blur_ksize or blur_ksize < 3 or blur_ksize % 2 == 0:
        return pil_img

    import cv2
    import numpy as np

    rgb = np.array(pil_img)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    bgr = cv2.GaussianBlur(bgr, (blur_ksize, blur_ksize), 0)
    rgb2 = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb2)


def preprocess_for_canny(pil_img: Image.Image, clahe: bool, sharpen: bool, denoise: bool) -> Image.Image:
    """
    Video-screenshot booster stack:
      - denoise  : removes compression grain
      - clahe    : boosts local contrast -> more detectable edges
      - sharpen  : light unsharp mask -> crisper edges
    """
    if not (clahe or sharpen or denoise):
        return pil_img

    import cv2
    import numpy as np

    rgb = np.array(pil_img.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    if denoise:
        # gentle defaults (keeps structure)
        bgr = cv2.fastNlMeansDenoisingColored(bgr, None, 5, 5, 7, 21)

    if clahe:
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe_op = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe_op.apply(l)
        lab = cv2.merge((l, a, b))
        bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    if sharpen:
        blur = cv2.GaussianBlur(bgr, (0, 0), 1.2)
        bgr = cv2.addWeighted(bgr, 1.35, blur, -0.35, 0)

    rgb2 = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb2)


def orientation_tag(w: int, h: int) -> str:
    # square counts as vertical (safe default)
    return "landscape" if w > h else "vertical"


def postprocess_canny(
    pil_img: Image.Image,
    invert: bool,
    thickness: str,
    adaptive: bool,
    clean_bg: bool,
    clean_thresh: int,
    speckle: str,
) -> Image.Image:
    """Optional post-processing to make Canny maps cleaner for ControlNet.

    - adaptive     : autocontrast before thresholding
    - clean_bg     : force pure black/white using a threshold
    - thickness    : thin/thicken edges using min/max filters
    - speckle      : median filter to reduce small artifacts
    - invert       : invert the final map
    """

    img = pil_img.convert("L")

    if adaptive:
        img = ImageOps.autocontrast(img)

    if clean_bg:
        t = int(max(0, min(255, clean_thresh)))
        img = img.point(lambda p: 255 if p >= t else 0)

    sp = (speckle or "none").lower()
    if sp == "median3":
        img = img.filter(ImageFilter.MedianFilter(size=3))
    elif sp == "median5":
        img = img.filter(ImageFilter.MedianFilter(size=5))

    th = (thickness or "none").lower()
    if th == "thin":
        img = img.filter(ImageFilter.MinFilter(size=3))
    elif th == "thick":
        img = img.filter(ImageFilter.MaxFilter(size=3))
    elif th == "extra_thick":
        img = img.filter(ImageFilter.MaxFilter(size=5))

    if invert:
        img = ImageOps.invert(img)

    # ControlNet is happiest with RGB PNGs.
    return img.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", default="", help="Input folder (ignored when --input is used)")
    ap.add_argument("--out_dir", required=True, help="Output folder")
    ap.add_argument("--input", default="", help="Single image path (optional)")
    ap.add_argument(
        "--input_rel",
        default="",
        help="Optional relative key for outputs when using --input (e.g. sub/dir/name.png)",
    )
    ap.add_argument("--mode", default="cover", choices=["cover", "contain"], help="How to fit input into target size")
    ap.add_argument("--detect", type=int, default=512, help="Detect resolution (lower = faster, may lose detail)")

    # OK Auto orientation sizes
    ap.add_argument("--portrait_size", default="896x1344", help="Output size for vertical images")
    ap.add_argument("--landscape_size", default="1344x896", help="Output size for landscape images")

    # OK Optional: overlay BEFORE detection (applies to both canny + openpose)
    ap.add_argument("--overlay_png", default="", help="PNG (with alpha) to overlay before detection")
    ap.add_argument(
        "--overlay_png_pos",
        default="bottom-right",
        choices=[
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "center",
            "top-center",
            "bottom-center",
        ],
        help="Overlay PNG anchor position",
    )
    ap.add_argument("--overlay_png_scale", type=float, default=0.25, help="Overlay PNG scale (fraction of base width)")
    ap.add_argument("--overlay_png_opacity", type=float, default=1.0, help="Overlay PNG opacity (0..1)")
    ap.add_argument("--overlay_png_offx", type=int, default=0, help="Overlay PNG X offset")
    ap.add_argument("--overlay_png_offy", type=int, default=0, help="Overlay PNG Y offset")

    ap.add_argument("--overlay_text", default="", help="Text to draw before detection")
    ap.add_argument("--overlay_text_size", type=int, default=28, help="Text size")
    ap.add_argument("--overlay_text_color", default="#FFFFFF", help="Text color hex")
    ap.add_argument("--overlay_text_outline", action="store_true", help="Text outline")
    ap.add_argument("--overlay_text_outline_color", default="#000000", help="Outline color hex")
    ap.add_argument(
        "--overlay_text_pos",
        default="bottom-right",
        choices=[
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "center",
            "top-center",
            "bottom-center",
        ],
        help="Text anchor position",
    )
    ap.add_argument("--overlay_text_offx", type=int, default=0, help="Text X offset")
    ap.add_argument("--overlay_text_offy", type=int, default=0, help="Text Y offset")

    # Canny thresholds + blur
    ap.add_argument("--canny_low", type=int, default=150, help="Canny low threshold")
    ap.add_argument("--canny_high", type=int, default=300, help="Canny high threshold")
    ap.add_argument("--blur", type=int, default=3, help="Pre-blur kernel size for Canny (odd: 0/3/5/7...)")

    # OK New: video-frame boosters for canny
    ap.add_argument("--clahe", action="store_true", help="Boost local contrast for better edges (Canny only)")
    ap.add_argument("--sharpen", action="store_true", help="Light unsharp mask before Canny")
    ap.add_argument("--denoise", action="store_true", help="Denoise before Canny (helps compression/grain)")

    # OK New: canny map cleanup (post-processing)
    ap.add_argument("--canny_invert", action="store_true", help="Invert final canny map")
    ap.add_argument(
        "--canny_thickness",
        default="none",
        choices=["none", "thin", "thick", "extra_thick"],
        help="Thin/thicken edges after detection",
    )
    ap.add_argument("--canny_adaptive", action="store_true", help="Autocontrast before thresholding")
    ap.add_argument("--canny_clean_bg", action="store_true", help="Force pure black/white background")
    ap.add_argument("--canny_clean_thresh", type=int, default=128, help="Threshold for clean background")
    ap.add_argument(
        "--canny_speckle",
        default="none",
        choices=["none", "median3", "median5"],
        help="Median filter to reduce speckles",
    )

    # Toggles
    ap.add_argument("--openpose", action="store_true", help="Generate openpose maps")
    ap.add_argument("--canny", action="store_true", help="Generate canny maps")
    ap.add_argument("--depth", action="store_true", help="Generate depth maps (MiDaS)")
    ap.add_argument("--name_suffix", action="store_true", help="Append _canny/_openpose/_depth to output filenames")


    # OpenPose options
    ap.add_argument("--hands", action="store_true", help="Openpose: include hands")
    ap.add_argument("--face", action="store_true", help="Openpose: include face")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Openpose device")

    # Depth options
    ap.add_argument("--depth_device", default="cpu", choices=["cpu", "cuda"], help="Depth device")
    ap.add_argument("--depth_invert", action="store_true", help="Invert depth map (optional)")

    ap.add_argument("--recursive", action="store_true", help="Scan subfolders")
    ap.add_argument("--skip_existing", action="store_true", help="Skip outputs that already exist")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    single_input = (args.input or "").strip()
    in_dir = Path(args.in_dir) if (args.in_dir or "").strip() else None

    portrait_w, portrait_h = parse_size(args.portrait_size)
    landscape_w, landscape_h = parse_size(args.landscape_size)

    # If user didn't specify any, do all.
    none_selected = (not args.canny and not args.openpose and not args.depth)
    do_canny = args.canny or none_selected
    do_openpose = args.openpose or none_selected
    do_depth = args.depth or none_selected

    canny_detector = CannyDetector() if do_canny else None

    openpose_detector = None
    if do_openpose:
        openpose_detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
        if hasattr(openpose_detector, "to"):
            openpose_detector = openpose_detector.to(args.device)

        # hands/face drawing may require matplotlib
        if (args.hands or args.face):
            try:
                import matplotlib  # noqa: F401
            except Exception:
                raise SystemExit(
                    "You enabled --hands/--face but matplotlib isn't installed.\n"
                    "Fix: cn_hints_env\\Scripts\\python.exe -m pip install -U matplotlib"
                )


    # --- DEPTH ---
    depth_detector = None
    if do_depth:
        try:
            depth_detector = MidasDetector.from_pretrained("lllyasviel/ControlNet")
        except Exception as e:
            raise SystemExit(
                "Depth detector failed to load. Install/upgrade controlnet-aux + torch in your chosen python env.\n"
                f"Error: {e}"
            )
        if hasattr(depth_detector, "to"):
            try:
                depth_detector = depth_detector.to(args.depth_device)
            except Exception:
                pass

    if single_input:
        img_p = Path(single_input)
        if not img_p.exists():
            raise SystemExit(f"Single input not found: {img_p}")
        images = [img_p]
    else:
        if in_dir is None or not in_dir.exists():
            raise SystemExit("You must set --in_dir (folder) unless using --input (single file).")
        images = list(iter_images(in_dir, args.recursive))
        if not images:
            raise SystemExit(f"No images found in: {in_dir}")

    for img_path in tqdm(images, desc="Processing"):
        if single_input:
            rel_key = (args.input_rel or "").strip()
            rel = Path(rel_key) if rel_key else Path(img_path.name)
        else:
            rel = img_path.relative_to(in_dir)

        stem = rel.with_suffix("")  # keep subfolder structure if provided

        try:
            img = Image.open(img_path)
        except Exception:
            continue

        in_w, in_h = img.size
        orient = orientation_tag(in_w, in_h)

        def out_path(kind: str):
            out_stem = stem
            if getattr(args, "name_suffix", False):
                out_stem = stem.with_name(stem.name + f"_{kind}")
            out_p = out_dir / kind / orient / out_stem
            out_p = out_p.with_suffix(".png")
            out_p.parent.mkdir(parents=True, exist_ok=True)
            return out_p


        # choose target size per orientation
        if orient == "vertical":
            tw, th = portrait_w, portrait_h
        else:
            tw, th = landscape_w, landscape_h

        prepped = fit_image(img, tw, th, args.mode)
        prepped = apply_overlays(prepped, args)

        # Keep output stable by using the min side as image_resolution
        image_resolution = min(tw, th)

        # --- CANNY ---
        if do_canny and canny_detector is not None:
            out_p = out_path("canny")

            if not (args.skip_existing and out_p.exists()):
                canny_base = preprocess_for_canny(prepped, args.clahe, args.sharpen, args.denoise)
                canny_input = apply_optional_blur(canny_base, args.blur)

                canny_img = canny_detector(
                    input_image=canny_input,
                    low_threshold=args.canny_low,
                    high_threshold=args.canny_high,
                    detect_resolution=args.detect,
                    image_resolution=image_resolution,
                    output_type="pil",
                )

                canny_img = postprocess_canny(
                    canny_img,
                    invert=args.canny_invert,
                    thickness=args.canny_thickness,
                    adaptive=args.canny_adaptive,
                    clean_bg=args.canny_clean_bg,
                    clean_thresh=args.canny_clean_thresh,
                    speckle=args.canny_speckle,
                )
                canny_img.save(out_p)

        # --- OPENPOSE ---
        if do_openpose and openpose_detector is not None:
            out_p = out_path("openpose")

            if not (args.skip_existing and out_p.exists()):
                pose_img = openpose_detector(
                    prepped,
                    detect_resolution=args.detect,
                    image_resolution=image_resolution,
                    include_body=True,
                    include_hand=args.hands,
                    include_face=args.face,
                    output_type="pil",
                )
                pose_img.save(out_p)

        # --- DEPTH ---
        if do_depth and depth_detector is not None:
            out_p = out_path("depth")

            if not (args.skip_existing and out_p.exists()):
                depth_img = depth_detector(
                    prepped,
                    detect_resolution=args.detect,
                    image_resolution=image_resolution,
                    output_type="pil",
                )
                try:
                    if getattr(args, "depth_invert", False):
                        depth_img = ImageOps.invert(depth_img.convert("L")).convert("RGB")
                except Exception:
                    pass
                depth_img.save(out_p)

    print("Done OK")
    print(f"Saved to: {out_dir}")


if __name__ == "__main__":
    main()
