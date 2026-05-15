import cv2
import numpy as np
import streamlit as st
from PIL import Image


def rotate_crop(image, rect, padding=10):
    center, size, angle = rect
    w, h = size

    if w < h:
        angle += 90
        w, h = h, w

    w = int(w + 2 * padding)
    h = int(h + 2 * padding)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image,
        M,
        (image.shape[1], image.shape[0]),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    cropped = cv2.getRectSubPix(rotated, (w, h), center)
    return cropped


def extract_document(image, padding, min_area_ratio):
    original = image.copy()

    # Resize for processing
    max_height = 900
    ratio = image.shape[0] / max_height
    resized = cv2.resize(image, (int(image.shape[1] / ratio), max_height))

    h, w = resized.shape[:2]
    img_area = h * w

    # GrabCut foreground segmentation
    mask = np.zeros((h, w), np.uint8)

    margin_x = int(w * 0.05)
    margin_y = int(h * 0.05)

    rect = (
        margin_x,
        margin_y,
        w - 2 * margin_x,
        h - 2 * margin_y
    )

    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    cv2.grabCut(
        resized,
        mask,
        rect,
        bgd_model,
        fgd_model,
        5,
        cv2.GC_INIT_WITH_RECT
    )

    fg_mask = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0
    ).astype("uint8")

    # Clean mask
    kernel = np.ones((9, 9), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(
        fg_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None, resized, fg_mask

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    best = None
    best_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < img_area * min_area_ratio:
            continue

        rect = cv2.minAreaRect(cnt)
        (_, _), (rw, rh), _ = rect

        if rw == 0 or rh == 0:
            continue

        aspect = max(rw, rh) / min(rw, rh)

        # DNI/card-like aspect ratio, but tolerant
        if 1.2 <= aspect <= 2.2:
            if area > best_area:
                best = rect
                best_area = area

    debug = resized.copy()

    if best is None:
        return None, debug, fg_mask

    box = cv2.boxPoints(best)
    box = np.intp(box)
    cv2.drawContours(debug, [box], 0, (0, 255, 0), 3)

    # Scale rectangle back to original image
    center, size, angle = best
    center = (center[0] * ratio, center[1] * ratio)
    size = (size[0] * ratio, size[1] * ratio)
    rect_original = (center, size, angle)

    cropped = rotate_crop(original, rect_original, padding=padding)

    return cropped, debug, fg_mask


st.title("ID document extractor")

uploaded_file = st.file_uploader(
    "Upload a photo of an ID document",
    type=["jpg", "jpeg", "png"]
)

st.sidebar.header("Settings")

padding = st.sidebar.slider(
    "Padding around document",
    0,
    80,
    25,
    5
)

min_area_ratio = st.sidebar.slider(
    "Minimum object area",
    0.01,
    0.50,
    0.05,
    0.01
)

if uploaded_file:
    pil_image = Image.open(uploaded_file).convert("RGB")
    image_rgb = np.array(pil_image)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    result, debug, mask = extract_document(
        image_bgr,
        padding=padding,
        min_area_ratio=min_area_ratio
    )

    st.subheader("Original")
    st.image(pil_image)

    st.subheader("Debug: detected document")
    st.image(cv2.cvtColor(debug, cv2.COLOR_BGR2RGB))

    st.subheader("Debug: foreground mask")
    st.image(mask, clamp=True)

    if result is not None:
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

        st.subheader("Extracted document")
        st.image(result_rgb)

        output = Image.fromarray(result_rgb)
        output.save("extracted_id.png")

        with open("extracted_id.png", "rb") as f:
            st.download_button(
                "Download extracted image",
                f,
                file_name="extracted_id.png",
                mime="image/png"
            )
    else:
        st.error("Could not detect the document. Try lowering Minimum object area.")