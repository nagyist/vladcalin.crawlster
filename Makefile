
.PHONY: docs

test:
	pytest tests/
	flake8 crawlster/


clean:
	find . -name "*.pyc" -delete


docs:
	$(MAKE) -C docs html


install_dev:
	pip install -e .
	pip install -r requirements/test.txt


release: release_minor

release_patch:
	bumpversion minor

release_minor:
	bumpversion minor

release_major:
	bumpversion major