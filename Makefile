# run these during dev 
# put assert 0 (or breakpoint() inside a worker thread) for a handy breakpoint
DEV_FILE=test_basic.py
DEV_FUNCTION=test_historical_data
dev:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb 
dev-info:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level INFO
dev-debug:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level DEBUG
dev-lab:
	@pytest "./tests/test_lab.py::test_ccxt" --pdb --log-cli-level INFO

# run all test cases with all debug message 
test:
	@pytest . --pdb
test-parallel:
	@pytest . --pdb --workers auto
test-debug:
	@pytest . --log-cli-level DEBUG

# generally, do these check before each major commit
test-and-checktype:
	@pytest . --pdb && mypy tests && mypy --strict trbox
test-parallel-and-checktype:
	@pytest . --pdb --workers auto && mypy tests && mypy --strict trbox
checktype:
	@mypy tests && mypy --strict trbox

# not test case but can be testing anything
demo:
	@python tests/demo.py

# regenerate the UML and package diagram
uml-diagrams:
	cd ./uml/ && \
	pyreverse -o png --colorized ../trbox && \
	cd ..

# scan for project requirements
requirements:
	@pipreqs ./trbox --savepath ./requirements.txt 
	@echo; echo 'requirements.txt:'; cat ./requirements.txt
requirements-print:
	@pipreqs ./trbox --print
