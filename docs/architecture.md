# Architecture Diagram

```mermaid
flowchart TD
    A[User pastes Job Description] --> C[React Frontend]
    B[User pastes/uploads Resume] --> C
    C --> D[FastAPI Backend]
    D --> E[Skill Extraction Engine]
    E --> F[Question Generator]
    F --> C
    C --> G[Candidate Answers]
    G --> H[Scoring Engine]
    H --> I[Gap Analyzer]
    I --> J[Learning Plan Generator]
    J --> K[Final Dashboard + JSON Export]
```

## Scoring Logic

Final Skill Score is computed from two signals:

- Resume Evidence Score: 40%
- Conversational Assessment Score: 60%

A skill is considered a gap if the final score is below 7/10.

The learning plan focuses on adjacent practical skills that the candidate can realistically acquire quickly through fundamentals, interview-style practice, and a mini project.
