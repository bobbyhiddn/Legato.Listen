#!/usr/bin/env python3
"""Register a signal from an artifact."""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from pathlib import Path

def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    import yaml
    try:
        frontmatter = yaml.safe_load(parts[1])
    except:
        frontmatter = {}

    return frontmatter or {}, parts[2].strip()

def generate_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI API."""
    import requests

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []

    response = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "text-embedding-3-small", "input": text}
    )

    if response.status_code == 200:
        return response.json()["data"][0]["embedding"]
    return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input artifact file")
    args = parser.parse_args()

    content = Path(args.input).read_text()
    frontmatter, body = extract_frontmatter(content)

    signal_id = frontmatter.get("id", f"unknown.{datetime.now().strftime('%Y%m%d%H%M%S')}")

    signal = {
        "id": signal_id,
        "type": "artifact",
        "source": "library",
        "category": frontmatter.get("category", "unknown"),
        "title": frontmatter.get("title", "Untitled"),
        "domain_tags": frontmatter.get("domain_tags", []),
        "intent": body[:200].replace("\n", " ").strip(),
        "key_phrases": frontmatter.get("key_phrases", []),
        "path": args.input,
        "created": frontmatter.get("created", datetime.utcnow().isoformat() + "Z"),
        "updated": datetime.utcnow().isoformat() + "Z",
    }

    # Generate embedding
    embed_text = f"{signal['title']} {signal['intent']} {' '.join(signal['key_phrases'])}"
    embedding = generate_embedding(embed_text)

    if embedding:
        import numpy as np
        embed_path = f"embeddings/{signal_id.replace('.', '-')}.npy"
        np.save(embed_path, np.array(embedding))
        signal["embedding_ref"] = embed_path

    # Update index
    index_path = Path("index.json")
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    index[signal_id] = signal
    index_path.write_text(json.dumps(index, indent=2))

    # Save full signal
    signal_path = Path(f"signals/library/{signal_id.split('.')[-1]}.json")
    signal_path.parent.mkdir(parents=True, exist_ok=True)
    signal_path.write_text(json.dumps(signal, indent=2))

    print(f"Registered: {signal_id}")

if __name__ == "__main__":
    main()
