.PHONY: install test deploy

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

test:
	.venv/bin/pytest tests/ -v

deploy:
	vercel --prod
