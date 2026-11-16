
## RAG Evaluation

Two chunking configurations were evaluated using 14 answerable questions.

| Configuration | Chunk Size | Overlap | Top K | Accuracy |
|---|---:|---:|---:|---:|
| A | 500 | 80 | 3 | 92.86% |
| B | 800 | 80 | 5 | 92.86% |

### Selected Configuration

- Chunk Size: 500
- Chunk Overlap: 80
- Top K: 3

### Evaluation Observations

- Both configurations achieved 13 correct retrievals out of 14.
- Article 12 was not retrieved in the top K results.
- Configuration A was selected because it uses fewer retrieved chunks while achieving the same accuracy.
- An out-of-scope question about purchasing property on Mars correctly returned "I don't know."

