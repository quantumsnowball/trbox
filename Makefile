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

# run all test cases with all debug message 
debug:
	@pytest . --log-cli-level DEBUG

# generally, do these check before each major commit
check:
	@pytest . --pdb && mypy tests && mypy --strict trbox
check-parallel:
	@pytest . --pdb --workers auto && mypy tests && mypy --strict trbox
check-type:
	@mypy tests && mypy --strict trbox

# regenerate the UML and package diagram
uml-diagrams:
	cd ./uml/ && \
	pyreverse -o png --colorized ../trbox && \
	cd ..
