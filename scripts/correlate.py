#!/usr/bin/env python3
"""Find correlated signals."""

import os
import sys
import json
import argparse
from pathlib import Path

import numpy as np

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

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
    parser.add_argument("--query", required=True, help="Query JSON")
    parser.add_argument("--output", required=True, help="Output file")
    args = parser.parse_args()

    query = json.loads(args.query)
    query_text = f"{query.get('title', '')} {query.get('intent', '')} {' '.join(query.get('key_phrases', []))}"

    query_embedding = generate_embedding(query_text)
    if not query_embedding:
        result = {"matches": [], "top_score": 0, "recommendation": "CREATE", "suggested_target": None}
        Path(args.output).write_text(json.dumps(result, indent=2))
        return

    index = json.loads(Path("index.json").read_text()) if Path("index.json").exists() else {}

    scores = []
    for signal_id, signal in index.items():
        if "embedding_ref" not in signal:
            continue
        try:
            stored = np.load(signal["embedding_ref"])
            score = cosine_similarity(query_embedding, stored)
            scores.append({"signal_id": signal_id, "score": score, "title": signal["title"], "path": signal["path"]})
        except:
            continue

    scores.sort(key=lambda x: x["score"], reverse=True)
    matches = scores[:5]
    top_score = matches[0]["score"] if matches else 0

    if top_score < 0.70:
        recommendation = "CREATE"
    elif top_score < 0.90:
        recommendation = "SUGGEST"
    else:
        recommendation = "AUTO-APPEND"

    result = {
        "matches": matches,
        "top_score": top_score,
        "recommendation": recommendation,
        "suggested_target": matches[0]["signal_id"] if matches else None
    }

    Path(args.output).write_text(json.dumps(result, indent=2))
    print(f"Correlation: {recommendation} (score: {top_score:.2f})")

if __name__ == "__main__":
    main()
