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

ethereum_classic: .git
	python3 analyse.py ethereum_classic

ethereum_classic_clean:
	rm -f ethereum_classic/parsed_data.json

clean:
	make bitcoin_clean
	make ethereum_clean
	make bitcoin_cash_clean
	make dogecoin_clean
	make cardano_clean
	make ethereum_classic_clean
