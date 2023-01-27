#
# Dev
#
# run these during dev 
# put assert 0 (or breakpoint() inside a worker thread) for a handy breakpoint
DEV_FILE=market/test_onrequest.py
DEV_FUNCTION=test_binance
# DEV_FILE=test_basic.py
# DEV_FUNCTION=test_dummy
# DEV_FILE=logger/test_logging.py
# DEV_FUNCTION=test_parser
dev:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb 
dev-info:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level INFO
dev-info-log:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level INFO --log-file log/dev-info.log
dev-debug:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level DEBUG
dev-debug-log:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level DEBUG --log-file log/dev-debug.log

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
typecheck:
	@mypy --strict trbox
typecheck-test:
	@mypy tests 
typecheck-everything: typecheck typecheck-test

#
# All
#
# test and check everything possible
test-and-typecheck: test typecheck typecheck-test
test-parallel-and-typecheck: test-parallel typecheck typecheck-test
typecheck-and-test: typecheck typecheck-test test
typecheck-and-test-parallel: typecheck typecheck-test test-parallel

#
# Logging
#
# generate pytest custom logger format string
#
log-formatter:
	@python trbox/common/logger.py
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
