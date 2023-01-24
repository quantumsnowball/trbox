# run this during dev, put assert 0 for a handy breakpoint
dev:
	@pytest ./tests/test_basic.py::test_historical_data --pdb --log-cli-level DEBUG

# run all test cases with all debug message 
debug:
	@pytest . --log-cli-level DEBUG

# generallyy, do this check before each commit
check:
	@pytest . --pdb && mypy tests && mypy --strict trbox

# regenerate the UML and package diagram
uml-diagrams:
	cd ./uml/ && \
	pyreverse -o png --colorized ../trbox && \
	cd ..
