test:
	pytest tests/
	pycodestyle crawlster/


clean:
	find . -name "*.pyc" -delete


install_dev:
	pip install -e .
	pip install -r requirements/test.txt



release_patch:
	bumpversion minor

release_minor:
	bumpversion minor

release_major:
	bumpversion major