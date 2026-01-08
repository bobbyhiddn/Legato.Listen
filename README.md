# Legato.Listen

> LEGATO Semantic Brain - Indexes artifacts and projects for semantic correlation.

## Structure

```
├── signals/
│   ├── library/    # Signals from Library artifacts
│   └── lab/        # Signals from Lab projects
├── embeddings/     # Vector embeddings for similarity search
├── scripts/        # Correlation and indexing scripts
└── index.json      # Master signal index
```

## Signal Format

```json
{
  "id": "library.epiphanies.oracle-machines",
  "type": "artifact",
  "source": "library",
  "category": "epiphany",
  "title": "Oracle Machines and AI Intuition",
  "domain_tags": ["ai", "turing", "theory"],
  "intent": "Exploring the connection between Turing's oracle machines and modern AI",
  "key_phrases": ["oracle machine", "intuition engine"],
  "path": "epiphanies/2026-01-07-oracle-machines.md",
  "created": "2026-01-07T15:30:00Z",
  "embedding_ref": "embeddings/library.epiphanies.oracle-machines.vec"
}
```

## Correlation Thresholds

| Score | Recommendation |
|-------|----------------|
| < 70% | CREATE new |
| 70-90% | SUGGEST (human review) |
| > 90% | AUTO-APPEND |

## Usage

Listen is queried by [Legato.Conduct](https://github.com/bobbyhiddn/Legato.Conduct) during transcript processing to prevent duplication and find related content.

---
*Part of the LEGATO system*
