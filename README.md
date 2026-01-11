# test_analysis_api

Internal FastAPI service that turns incorrectly answered questions into grouped weaknesses.

## Endpoints
- `GET /health`
- `POST /test-analysis`

## Request
```json
{
  "incorrect_cases": [
    {
      "questionId": 123,
      "question": "...",
      "student_answer": "...",
      "correct_answer": "...",
      "choices": ["A", "B", "C", "D"]
    }
  ]
}
```

Optional: provide `model_name` to override the default Gemini model.

## Response
```json
{
  "weaknesses": [
    {
      "id": "uuid",
      "weakness": "...",
      "pattern_type": "language",
      "description": "...",
      "evidence_question_ids": [123],
      "frequency": 1
    }
  ]
}
```

## Local run
```bash
export GOOGLE_API_KEY="..."
uvicorn app.main:app --host 0.0.0.0 --port 8080
```
