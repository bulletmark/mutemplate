NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))

check:: test
	ruff check $(NAME)/*.py
	flake8 $(NAME)/*.py
	mypy $(NAME)/*.py
	pyright $(NAME)/*.py
	vermin -vv --no-tips -i $(NAME)/*.py

build::
	rm -rf dist
	python3 -m build

upload: build
	twine3 upload dist/*

doc::
	update-readme-usage -a

test::
	cd test && make test

clean::
	@rm -vrf *.egg-info .venv/ build/ dist/ __pycache__ $(NAME)/__pycache__ test/templates.py
