PYFILES := `echo */*.py`
SHFILES := `echo */*.sh`

check:
  ruff check {{PYFILES}}
  ty check {{PYFILES}}
  vermin -vv --no-tips -i {{PYFILES}}
  md-link-checker
  shellcheck {{SHFILES}}

build:
  rm -rf dist
  uv build

upload: build
  uv-publish

doc:
  update-readme-usage

test:
  cd test && just test

format:
  ruff check --select I --fix {{PYFILES}} && ruff format {{PYFILES}}

clean:
	@rm -vrf *.egg-info .venv/ build/ dist/ __pycache__ */__pycache__ test/templates.py

# vim: se sw=2:
