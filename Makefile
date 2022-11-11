ALL:
	python3 analyse.py bitcoin

parse:
	make clean
	python3 bitcoin/parse.py

clean:
	rm -f bitcoin/parsed_data.json bitcoin/pool_addresses.json bitcoin/unmatched_tags
