ALL:

bitcoin: .git
	python3 analyse.py bitcoin

bitcoin_clean:
	rm -f bitcoin/parsed_data.json bitcoin/pool_addresses.json bitcoin/unmatched_tags

ethereum: .git
	python3 analyse.py ethereum

ethereum_clean:
	rm -f ethereum/parsed_data.json ethereum/pool_addresses.json ethereum/unmatched_tags

bitcoin_cash: .git
	python3 analyse.py bitcoin_cash

bitcoin_cash_clean:
	rm -f bitcoin_cash/parsed_data.json bitcoin_cash/pool_addresses.json bitcoin_cash/unmatched_tags

dogecoin: .git
	python3 analyse.py dogecoin

dogecoin_clean:
	rm -f dogecoin/parsed_data.json dogecoin/pool_addresses.json dogecoin/unmatched_tags

cardano: .git
	python3 analyse.py cardano

cardano_clean:
	rm -f cardano/parsed_data.json

clean:
	make clean_bitcoin
	make clean_ethereum
	make clean_bitcoin_cash
	make clean_dogecoin
	make clean_cardano
