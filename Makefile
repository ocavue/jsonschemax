init:
	pipenv install --dev

test:
	pipenv run mypy . --ignore-missing-imports
	pipenv run python3 -m unittest discover -s ./tests

format:
	pipenv run isort --recursive --atomic -y
	pipenv run black .
