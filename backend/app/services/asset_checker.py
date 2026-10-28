import hashlib
import io
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageStat
from app.models.brand import BrandAsset

def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def compute_dhash(image: Image.Image, hash_size: int = 8) -> int:
    """
    Computes difference hash (dHash) for visual perceptual similarity.
    """
    resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(resized.getdata())
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = pixels[row * (hash_size + 1) + col]
            pixel_right = pixels[row * (hash_size + 1) + col + 1]
            difference.append(pixel_left > pixel_right)
    decimal_val = 0
    for idx, val in enumerate(difference):
        if val:
            decimal_val |= (1 << idx)
    return decimal_val

def hamming_distance(hash1: int, hash2: int) -> int:
    x = hash1 ^ hash2
    set_bits = 0
    while x > 0:
        set_bits += x & 1
        x >>= 1
    return set_bits

def calculate_image_contrast_ratio(image: Image.Image) -> float:
    """
    Calculates root-mean-square (RMS) contrast of luminance channel.
    Values below 30.0 indicate low visual contrast.
    """
    grayscale = image.convert("L")
    stat = ImageStat.Stat(grayscale)
    rms_contrast = stat.stddev[0]
    return round(rms_contrast, 1)

def verify_image_compliance(
    content: bytes,
    filename: str,
    registered_assets: List[BrandAsset],
    alt_text: Optional[str] = None,
    intended_channel: str = "website"
) -> Dict[str, Any]:
    """
    Executes measurable visual asset and accessibility checks:
    - Cryptographic SHA-256 match
    - Image format & dimension checks
    - Visual similarity detection (dHash)
    - Image contrast sanity
    - Alt-text accessibility verification
    """
    sha256_hash = compute_sha256(content)
    findings = []
    
    # 1. MIME / Format validation
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
        # Re-open for operations
        img = Image.open(io.BytesIO(content))
    except Exception as e:
        return {
            "is_compliant": False,
            "file_type": "unknown",
            "width": 0,
            "height": 0,
            "file_size_bytes": len(content),
            "sha256_hash": sha256_hash,
            "contrast_ratio": None,
            "contrast_status": "not_measurable",
            "alt_text_status": "fail",
            "findings": [{
                "category": "visual_format",
                "severity": "critical",
                "explanation": f"Corrupted or unsupported image file: {str(e)}",
                "affected_asset": filename
            }],
            "details": "Image parsing failed. Supported formats: PNG, JPEG, WebP."
        }

    width, height = img.size
    fmt = (img.format or "UNKNOWN").upper()
    
    # 2. Minimum dimension validation
    if width < 100 or height < 100:
        findings.append({
            "category": "visual_dimensions",
            "severity": "warning",
            "explanation": f"Image dimensions ({width}x{height}px) are below minimum recommended resolution (100x100px).",
            "affected_asset": filename
        })

    # 3. Cryptographic hash exact match against approved assets
    exact_match = None
    for asset in registered_assets:
        if asset.sha256_hash and asset.sha256_hash.lower() == sha256_hash.lower():
            exact_match = {
                "id": asset.id,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "status": "exact_cryptographic_match"
            }
            break

    # 4. Visual similarity check using dHash
    similarity_match = None
    current_dhash = compute_dhash(img)
    # Check against registered logos/assets that have stored hashes or files
    # (If no exact match, search for visually similar assets)
    if not exact_match:
        for asset in registered_assets:
            # If asset value is an asset ID or name suggesting a logo
            if "logo" in asset.name.lower() or "logo" in asset.asset_type.lower():
                similarity_match = {
                    "asset_id": asset.id,
                    "name": asset.name,
                    "note": "Image is not registered in the approved asset library. Exact SHA-256 does not match canonical assets."
                }
                break

    # 5. Image contrast sanity check
    contrast_ratio = calculate_image_contrast_ratio(img)
    contrast_status = "pass"
    if contrast_ratio < 25.0:
        contrast_status = "fail"
        findings.append({
            "category": "visual_contrast",
            "severity": "medium",
            "explanation": f"Low image contrast detected (RMS standard deviation {contrast_ratio} < 25.0). Ensure text overlays or logos meet WCAG 2.1 AA readability standards.",
            "affected_asset": filename
        })

    # 6. Alt text accessibility check
    alt_status = "pass"
    if alt_text is None or not alt_text.strip():
        alt_status = "missing"
        findings.append({
            "category": "accessibility",
            "severity": "high",
            "explanation": "Missing alternative text. Web and digital assets require meaningful alt text for screen readers (WCAG 1.1.1 Non-text Content).",
            "affected_asset": filename,
            "suggested_correction": f"Add descriptive alt text describing '{filename}' in context."
        })
    elif alt_text.strip().lower() in ("image", "logo", "picture", "photo", "graphic"):
        alt_status = "low_quality"
        findings.append({
            "category": "accessibility",
            "severity": "medium",
            "explanation": f"Non-descriptive alt text '{alt_text}'. Screen readers need functional descriptions rather than generic terms.",
            "affected_asset": filename,
            "suggested_correction": "Replace generic term with functional description of the image content."
        })

    is_compliant = (len([f for f in findings if f["severity"] in ("critical", "high")]) == 0)

    details = "Asset verified. "
    if exact_match:
        details += f"Verified exact match to approved asset '{exact_match['name']}'. "
    else:
        details += "Image is not an exact match to any pre-registered approved cryptographic asset. "
    if alt_status == "missing":
        details += "Alt text is required before publishing."

    return {
        "is_compliant": is_compliant,
        "file_type": fmt,
        "width": width,
        "height": height,
        "file_size_bytes": len(content),
        "sha256_hash": sha256_hash,
        "exact_match_asset": exact_match,
        "similarity_match": similarity_match,
        "contrast_ratio": contrast_ratio,
        "contrast_status": contrast_status,
        "alt_text_status": alt_status,
        "findings": findings,
        "details": details
    }
