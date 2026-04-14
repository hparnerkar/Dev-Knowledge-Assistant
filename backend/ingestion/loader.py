"""
loader.py
Loads documents from a directory into LangChain Document objects.
Supports .txt, .md, and .pdf files.
"""

import logging
import os
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    PyPDFLoader,
)

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
    ".pdf": PyPDFLoader,
}


def load_documents(directory: str) -> List[Document]:
    """
    Recursively loads all supported documents from a directory.

    Args:
        directory: Path to the directory containing source documents.

    Returns:
        List of LangChain Document objects with content and metadata.

    Raises:
        FileNotFoundError: If the directory does not exist.
        ValueError: If no supported files are found.
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    documents: List[Document] = []
    skipped: List[str] = []

    for file_path in sorted(dir_path.rglob("*")):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        loader_cls = SUPPORTED_EXTENSIONS.get(ext)

        if loader_cls is None:
            skipped.append(file_path.name)
            continue

        try:
            logger.info(f"Loading: {file_path.name}")
            loader = loader_cls(str(file_path))
            docs = loader.load()

            # Enrich metadata with file info
            for doc in docs:
                doc.metadata.update({
                    "source": file_path.name,
                    "source_path": str(file_path),
                    "file_type": ext.lstrip("."),
                    "file_size_bytes": file_path.stat().st_size,
                })

            documents.extend(docs)
            logger.info(f"  ✓ Loaded {len(docs)} page(s) from {file_path.name}")

        except Exception as e:
            logger.error(f"  ✗ Failed to load {file_path.name}: {e}")
            continue

    if skipped:
        logger.info(f"Skipped {len(skipped)} unsupported file(s): {skipped}")

    if not documents:
        raise ValueError(
            f"No supported documents found in '{directory}'. "
            f"Supported formats: {list(SUPPORTED_EXTENSIONS.keys())}"
        )

    logger.info(f"Total documents loaded: {len(documents)}")
    return documents
