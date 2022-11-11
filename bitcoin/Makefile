ALL: *.json
	python3 analyse.py

parse:
	make clean
	python3 parse.py

clean:
	rm -f bitcoin_parsed_data.json bitcoin_pool_addresses.json bitcoin_unmatched_tags
