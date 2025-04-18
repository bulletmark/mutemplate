NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))
PYFILES = $(wildcard $(NAME)/*.py)

check: test
	ruff check $(PYFILES)
	mypy $(PYFILES)
	pyright $(PYFILES)

build:
	rm -rf dist
	uv build

upload: build
	uv-publish

doc:
	update-readme-usage -a

test::
	cd test && make test

format:
	ruff check --select I --fix $(PYFILES) && ruff format $(PYFILES)

clean:
	@rm -vrf *.egg-info .venv/ build/ dist/ __pycache__ $(NAME)/__pycache__ test/templates.py
