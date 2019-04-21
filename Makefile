install:
	pipenv install --dev --pre

lint:
	pipenv run flake8 ./**/*.py --max-line-length=100 --extend-ignore=E203
	pipenv run mypy . --ignore-missing-imports

test:
	pipenv run python3 -m unittest discover -s ./tests

format:
	pipenv run isort --recursive --atomic -y --skip .venv
	pipenv run black .

build:
	pipenv run python3 setup.py sdist bdist_wheel
	rm -rf build

release:
	pipenv run twine upload dist/* --skip-existing --verbose
