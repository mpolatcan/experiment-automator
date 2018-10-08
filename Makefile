all:
	python3 -m pip install --upgrade setuptools wheel
	python3 setup.py sdist bdist_wheel
	python3 -m pip install --upgrade twine
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	sudo rm -r build dist

test-install:
	python3 -m pip install --index-url https://test.pypi.org/simple/ ml-notifier
