ALL:

bitcoin: .git
	python3 analyse.py bitcoin

parse_bitcoin:
	make clean_bitcoin
	python3 bitcoin/parse.py

clean:
	make clean_bitcoin

clean_bitcoin:
	rm -f bitcoin/parsed_data.json bitcoin/pool_addresses.json bitcoin/unmatched_tags
