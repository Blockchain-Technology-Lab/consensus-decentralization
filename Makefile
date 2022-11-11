ALL:

bitcoin: .git
	python3 analyse.py bitcoin

parse_bitcoin:
	make clean_bitcoin
	python3 bitcoin/parse.py

ethereum: .git
	python3 analyse.py ethereum

parse_ethereum:
	make clean_ethereum
	python3 ethereum/parse.py

clean:
	make clean_bitcoin
	make clean_ethereum

clean_bitcoin:
	rm -f bitcoin/parsed_data.json bitcoin/pool_addresses.json bitcoin/unmatched_tags

clean_ethereum:
	rm -f ethereum/parsed_data.json ethereum/pool_addresses.json ethereum/unmatched_tags
