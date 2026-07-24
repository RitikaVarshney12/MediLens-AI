import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from functools import lru_cache
from typing import Callable, TypeVar

import fitz  # PyMuPDF

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

# A PDF text layer shorter than this is treated as "no real text" (e.g. a
# scanned PDF where only a page number or watermark is selectable), and
# falls through to OCR instead.
MIN_TEXT_LAYER_CHARS = 20


class OcrError(Exception):
    pass


@lru_cache(maxsize=1)
def _get_reader():
    # Deferred import: easyocr (and its torch dependency) is only needed
    # once OCR actually runs, so the rest of the app can boot without it
    # installed, and the (slow) model load only happens once per process.
    import easyocr

    return easyocr.Reader(settings.OCR_LANGUAGES, gpu=settings.OCR_GPU)


def _extract_pdf_text_layer(content: bytes) -> str:
    with fitz.open(stream=content, filetype="pdf") as doc:
        pages = [page.get_text("text") for page in doc]
    return "\n".join(pages).strip()


def _rasterize_pdf_pages(content: bytes, dpi: int = 200) -> list[bytes]:
    images: list[bytes] = []
    with fitz.open(stream=content, filetype="pdf") as doc:
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        for page in doc:
            pixmap = page.get_pixmap(matrix=matrix)
            images.append(pixmap.tobytes("png"))
    return images


def _run_easyocr_on_image_bytes(image_bytes: bytes) -> str:
    reader = _get_reader()
    results = reader.readtext(image_bytes, detail=0, paragraph=True)
    return "\n".join(results)


def _with_timeout(fn: Callable[[], T], timeout_seconds: int) -> T:
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn)
    try:
        result = future.result(timeout=timeout_seconds)
    except FutureTimeoutError as exc:
        # Do NOT use `with ThreadPoolExecutor()` here: its __exit__ calls
        # shutdown(wait=True), which blocks until the runaway thread
        # actually finishes - silently defeating the timeout. A running
        # thread can't be force-killed via this API, so instead we stop
        # waiting immediately and let the orphaned thread finish on its
        # own in the background.
        executor.shutdown(wait=False)
        raise OcrError("OCR timed out") from exc
    else:
        executor.shutdown(wait=False)
        return result


def _extract_text_once(content: bytes, file_type: str) -> str:
    file_type = file_type.lower()

    if file_type == "pdf":
        try:
            text_layer = _extract_pdf_text_layer(content)
        except Exception as exc:
            raise OcrError(f"Failed to read PDF: {exc}") from exc

        if len(text_layer) >= MIN_TEXT_LAYER_CHARS:
            return text_layer

        try:
            page_images = _rasterize_pdf_pages(content)
        except Exception as exc:
            raise OcrError(f"Failed to rasterize PDF for OCR: {exc}") from exc

        def run_ocr_all_pages() -> str:
            texts = [_run_easyocr_on_image_bytes(image) for image in page_images]
            return "\n".join(texts)

        return _with_timeout(run_ocr_all_pages, settings.OCR_TIMEOUT_SECONDS)

    if file_type in {"jpg", "jpeg", "png"}:
        try:
            return _with_timeout(
                lambda: _run_easyocr_on_image_bytes(content), settings.OCR_TIMEOUT_SECONDS
            )
        except OcrError:
            raise
        except Exception as exc:
            raise OcrError(f"Failed to OCR image: {exc}") from exc

    raise OcrError(f"Unsupported file type for OCR: {file_type}")


def extract_text(content: bytes, file_type: str) -> str:
    """Extract text with retry, per settings.OCR_MAX_RETRIES."""
    last_error: OcrError | None = None

    for attempt in range(1, settings.OCR_MAX_RETRIES + 1):
        try:
            return _extract_text_once(content, file_type)
        except OcrError as exc:
            last_error = exc
            logger.warning(
                "OCR attempt %s/%s failed for file_type=%s: %s",
                attempt,
                settings.OCR_MAX_RETRIES,
                file_type,
                exc,
            )

    assert last_error is not None
    raise last_error