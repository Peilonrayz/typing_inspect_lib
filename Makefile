init:
	pip install pipenv
	pipenv install --dev

test:
	pipenv run python -m unittest discover -s ./tests -t .