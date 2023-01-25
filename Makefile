#
# Dev
#
# run these during dev 
# put assert 0 (or breakpoint() inside a worker thread) for a handy breakpoint
DEV_FILE=market/test_onrequest.py
DEV_FUNCTION=test_binance
dev:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb 
dev-info:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level INFO
dev-debug:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level DEBUG

#
# lab
#
# dev lab playground
dev-lab-ccxt:
	@pytest "./tests/lab/test_ccxt.py::test_ccxt" --pdb --log-cli-level INFO
dev-lab-binance-restful:
	@pytest "./tests/lab/test_python_binance::test_binance_restful" --pdb --log-cli-level INFO
dev-lab-binance-websocket:
	@pytest "./tests/lab/test_python_binance.py::test_binance_websocket" --pdb --log-cli-level INFO
dev-lab-binance-connector-python-restful:
	@pytest "./tests/lab/test_binance_connector_python.py::test_restful" --pdb --log-cli-level INFO
dev-lab-binance-connector-python-websocket:
	@pytest "./tests/lab/test_binance_connector_python.py::test_websocket" --pdb --log-cli-level INFO

#
# Testing
#
# run all test cases with all debug message 
test:
	@pytest . -k 'not lab' --pdb
test-debug:
	@pytest . -k 'not lab' --pdb --log-cli-level DEBUG
test-parallel:
	@pytest . -k 'not lab' --pdb --workers auto

#
# Typecheck
#
# generally, do these check before each major commit
test-and-checktype:
	@pytest . --pdb && mypy tests && mypy --strict trbox
test-parallel-and-checktype:
	@pytest . --pdb --workers auto && mypy tests && mypy --strict trbox
checktype:
	@mypy tests; mypy --strict trbox

#
# Demo
#
# not test case but can be testing anything
demo:
	@python tests/demo.py

#
# UML diagrams gen
#
# regenerate the UML and package diagram
uml-diagrams:
	cd ./uml/ && \
	pyreverse -o png --colorized ../trbox && \
	cd ..

#
# Pip requirements gen
#
# scan for project requirements
requirements:
	@pipreqs ./trbox --savepath ./requirements.txt 
	@echo; echo 'requirements.txt:'; cat ./requirements.txt
requirements-print:
	@pipreqs ./trbox --print
