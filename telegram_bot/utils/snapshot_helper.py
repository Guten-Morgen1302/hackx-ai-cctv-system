"""
utils/snapshot_helper.py
Finds the best matching snapshot image for a given track ID.
"""

import os
import re
import glob
from pathlib import Path


def get_snapshot_for_id(snapshots_dir: str, track_id: int) -> str | None:
    """
    Search snapshots_dir for an image that contains the track ID in its filename.
    Patterns tried (in order):
      - id_{id} / track_{id} / _{id}. anywhere in filename
      - fallback: most recent image in folder

    Returns the absolute path to the matched image, or None if folder is empty.
    """
    if not os.path.isdir(snapshots_dir):
        return None

    # Collect all image files
    images = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
        images.extend(glob.glob(os.path.join(snapshots_dir, ext)))
        images.extend(glob.glob(os.path.join(snapshots_dir, ext.upper())))

    if not images:
        return None

    # Sort by modification time, newest first
    images.sort(key=lambda p: os.path.getmtime(p), reverse=True)

    # Try to find one matching the track_id
    patterns = [
        rf"id[_-]0*{track_id}[._\-]",
        rf"track[_-]0*{track_id}[._\-]",
        rf"_0*{track_id}\.",
        rf"_0*{track_id}$",
        rf"f0*{track_id}\.",   # frame-numbered files like objects_..._f11.png
    ]
    for img in images:
        fname = os.path.basename(img).lower()
        for pat in patterns:
            if re.search(pat, fname):
                return img

    # Fallback: return the most recent image regardless
    return images[0]
