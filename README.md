# Agent Lab Method

Minimal read-only method package extracted from `agent-lab-console`.

It contains the shared run schema, the synthetic GenMentor adapter, and synthetic fixtures. It does not contain private runs, replay archives, deployment runners, credentials, prompts, or model responses.

```bash
python -m venv .venv
.venv/bin/pip install -e ".[test]" -i https://pypi.tuna.tsinghua.edu.cn/simple
.venv/bin/python -m pytest -q
```
