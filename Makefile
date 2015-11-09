
check:
	PYTHONPATH=. pylint bin/lbng lbng
	pep8 bin/lbng lbng

