ALL:

bitcoin: .git
	python3 analyse.py bitcoin

parse_bitcoin:
	make clean_bitcoin
	python3 bitcoin/parse.py

clean_bitcoin:
	rm -f bitcoin/parsed_data.json bitcoin/pool_addresses.json bitcoin/unmatched_tags

ethereum: .git
	python3 analyse.py ethereum

parse_ethereum:
	make clean_ethereum
	python3 ethereum/parse.py

clean_ethereum:
	rm -f ethereum/parsed_data.json ethereum/pool_addresses.json ethereum/unmatched_tags

bitcoin_cash: .git
	python3 analyse.py bitcoin_cash

parse_bitcoin:
	make clean_bitcoin_cash
	python3 bitcoin_cash/parse.py

clean_bitcoin_cash:
	rm -f bitcoin_cash/parsed_data.json bitcoin_cash/pool_addresses.json bitcoin_cash/unmatched_tags

clean:
	make clean_bitcoin
	make clean_ethereum
	make clean_bitcoin_cash
