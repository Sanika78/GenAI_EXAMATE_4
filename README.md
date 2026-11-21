## Checkpoint 2 – Streamlit UI
![CI](https://github.com/Sanika78/GenAI_EXAMATE_4/actions/workflows/ci.yml/badge.svg)
SamvidhanSathi now includes an interactive Streamlit interface.

### Features
- AI-powered Constitution Q&A
- RAG and Agent assistant modes
- Source citations
- Thumbs up/down feedback collection
- Article Card with original constitutional text
- Plain-English Article explanations
- Amendment history footnotes

### Application Screenshot

![SamvidhanSathi Checkpoint 2](screenshots/checkpoint-2.png)

### Run the Application

Start the FastAPI backend:

```bash
uvicorn app.main:app --reload

Save the file.

### Step 2: Commit and push

Run:

```powershell
git add README.md
git commit -m "docs: add development checks"
git push origin feature/day-12-ci-demo


## Development Checks

Run code quality checks:

```bash
ruff check .


### Then save and run these commands in PowerShell:

```powershell
git add README.md
git commit -m "docs: add development checks"
git push origin feature/day-12-ci-demo


## Day 12 - CI/CD

- Automated testing using GitHub Actions.
- Code quality checks using Ruff.
- Automated tests using Pytest.
- Docker image build verification.


## Live Deployment

## Live Deployment

SamvidhanSathi is deployed on Render.

- **Live API:** https://samvidhansathi-api.onrender.com
- **Health Check:** https://samvidhansathi-api.onrender.com/health
- **API Documentation:** https://samvidhansathi-api.onrender.com/docs

**Deployment Status:** Live



## Production Notes

### Performance Monitoring

SamvidhanSathi includes FastAPI middleware to log request latency and HTTP status codes.

Example measured results:

| Metric | Measured Result |
|---|---:|
| Health endpoint latency | 82.41 ms |
| First `/chat` request (cache MISS) | 3069.80 ms |
| Repeated `/chat` request (cache HIT) | 39.96 ms |
| Cache hit latency reduction | 98.7% |

### LLM Token Monitoring

Token usage is captured from provider response metadata.

| Provider | Input Tokens | Output Tokens | Total |
|---|---:|---:|---:|
| Groq – first measured request | 358 | 450 | 808 |

### Caching

- Implemented an in-memory response cache.
- Maximum cache capacity: 100 entries.
- Repeated questions with the same prompt version reuse cached responses.
- Cache entries are cleared when the application restarts.

### Input Validation

- Maximum question length: 2,000 characters.
- Prompt version restricted to 1 or 2.
- RAG top_k restricted to 1–10.
- Agent thread ID limited to 100 characters.

### Security Testing

- Added a prompt-injection unit test.
- Verified that Constitution-only grounding instructions remain in the constructed prompt.
- Test result: 1 passed.
