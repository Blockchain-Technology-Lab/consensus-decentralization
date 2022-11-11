ALL:
	python3 analyse.py

parse:
	make clean
	cd bitcoin && python3 parse.py

clean:
	rm -f bitcoin/parsed_data.json bitcoin/pool_addresses.json bitcoin/unmatched_tags
