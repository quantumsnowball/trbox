#
# Dev
#
# run these during dev 
# put assert 0 (or breakpoint() inside a worker thread) for a handy breakpoint
# DEV_FILE=market/test_market.py
DEV_FILE=market/binance/test_historical.py
# DEV_FUNCTION=test_binance_trade_streaming
# DEV_FUNCTION=test_binance_kline_streaming
# DEV_FILE=playground/test_dev.py
# DEV_FILE=test_trader.py
# DEV_FILE=test_backtest.py
# DEV_FILE=strategy/test_count.py
# DEV_FILE=market/test_utils.py
DEV_FUNCTION=test_historical_data
# DEV_FUNCTION=test_dummy
# DEV_FUNCTION=test_historical_data
# DEV_FUNCTION=test_count
# DEV_FUNCTION=test_combined_rolling_windows


dev:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb 
dev-warning:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level WARNING
dev-warning-log:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level WARNING --log-file-level INFO --log-file log/dev-warning.log
dev-info:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level INFO
dev-info-log:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level INFO --log-file log/dev-info.log
dev-debug:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level DEBUG
dev-debug-log:
	@pytest "./tests/${DEV_FILE}::${DEV_FUNCTION}" --pdb --log-cli-level DEBUG --log-file log/dev-debug.log

#
# playground
#
# dev playground
dev-playground-ccxt:
	@pytest "./tests/playground/test_ccxt.py::test_ccxt" --pdb --log-cli-level INFO
dev-playground-binance-restful:
	@pytest "./tests/playground/test_python_binance::test_binance_restful" --pdb --log-cli-level INFO
dev-playground-binance-websocket:
	@pytest "./tests/playground/test_python_binance.py::test_binance_websocket" --pdb --log-cli-level INFO
dev-playground-binance-connector-python-restful:
	@pytest "./tests/playground/test_binance_connector_python.py::test_restful" --pdb --log-cli-level INFO
dev-playground-binance-connector-python-websocket:
	@pytest "./tests/playground/test_binance_connector_python.py::test_websocket" --pdb --log-cli-level INFO
dev-playground-binance-testnet-exchange-info:
	@pytest "./tests/playground/binance_testnet/test_restful.py::test_exchange_info" --pdb --log-cli-level INFO
dev-playground-binance-testnet-account-balance:
	@pytest "./tests/playground/binance_testnet/test_restful.py::test_account_balance" --pdb --log-cli-level INFO
dev-playground-binance-testnet-account-worth:
	@pytest "./tests/playground/binance_testnet/test_restful.py::test_account_worth" --pdb --log-cli-level INFO
dev-playground-binance-testnet-market-order:
	@pytest "./tests/playground/binance_testnet/test_restful.py::test_market_order" --pdb --log-cli-level INFO
dev-playground-binance-testnet-limit-order:
	@pytest "./tests/playground/binance_testnet/test_restful.py::test_binance_testnet.py::test_limit_order" --pdb --log-cli-level INFO
dev-playground-binance-testnet-cancel-all-open-order:
	@pytest "./tests/playground/binance_testnet/test_restful.py::test_cancel_all_open_order" --pdb --log-cli-level INFO
dev-playground-binance-testnet-current-open-order:
	@pytest "./tests/playground/binance_testnet/test_restful.py::test_current_open_order" --pdb --log-cli-level INFO

#
# Testing
#
# run all test cases with all debug message 
test:
	@pytest tests/ -k 'not playground' --pdb
test-debug:
	@pytest tests/ -k 'not playground' --pdb --log-cli-level DEBUG
test-parallel:
	@pytest tests/ -k 'not playground' --workers auto --verbose

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
change-pytest-log-format:
	@python trbox/common/logger/__init__.py
# Demo
#
# not test case but can be testing anything
demo:
	@python tests/demo.py
demo-websocket-chat:
	@python tests/playground/websocket/socket-chat.py
demo-gunicorn:
	@gunicorn -b 127.0.0.1:5000 --workers 4 --threads 4 trbox.console.flask_sock:app

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
