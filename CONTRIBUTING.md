# Contributing

## Branches

Use one branch per owner and topic: `prem/eda`, `yahya/forecast`,
`vishal/anomaly`, or `rayyan/pipeline`. Do not commit directly to `main`.
Shared code belongs in `src/`; use `get_train_test()` rather than creating a
new split in a notebook.

## Pull requests

Open each PR against `main`, link its issue, and tick only completed items in
`CHECKLIST.md`. Keep commits small and use `feat:`, `fix:`, `docs:`, `ci:`, or
`test:` prefixes. Include plot screenshots where relevant and confirm the
notebook runs from a fresh clone.

Before requesting review, rebase on `main`, run `ruff check src/`, `pytest`,
and the affected notebook. One teammate approval and passing CI are required.
Use squash merge only, delete the branch after merge, and never merge without
Rayyan's approval.

Never commit raw data, `.env` files, API keys, or notebook outputs larger than
5 MB. Configure the OpenAQ API key only through `OPENAQ_API_KEY`.
