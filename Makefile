init:
	pipenv install --dev

test:
	pipenv run mypy . --ignore-missing-imports
	pipenv run python3 -m unittest discover -s ./tests

format:
	pipenv run isort --recursive --atomic -y --skip .venv
	pipenv run black .

build:
	pipenv run python3 setup.py sdist bdist_wheel

upload:
	pipenv run twine upload dist/*
