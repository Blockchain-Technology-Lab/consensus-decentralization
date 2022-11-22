ALL:

bitcoin: .git
	python3 analyse.py bitcoin

bitcoin_clean:
	rm -f bitcoin/parsed_data.json bitcoin/pool_addresses.json

ethereum: .git
	python3 analyse.py ethereum

ethereum_clean:
	rm -f ethereum/parsed_data.json ethereum/pool_addresses.json

bitcoin_cash: .git
	python3 analyse.py bitcoin_cash

bitcoin_cash_clean:
	rm -f bitcoin_cash/parsed_data.json bitcoin_cash/pool_addresses.json

dogecoin: .git
	python3 analyse.py dogecoin

dogecoin_clean:
	rm -f dogecoin/parsed_data.json dogecoin/pool_addresses.json

cardano: .git
	python3 analyse.py cardano

cardano_clean:
	rm -f cardano/parsed_data.json

ethereum_classic: .git
	python3 analyse.py ethereum_classic

ethereum_classic_clean:
	rm -f ethereum_classic/parsed_data.json ethereum_classic/pool_addresses.json

litecoin: .git
	python3 analyse.py litecoin

litecoin_clean:
	rm -f litecoin/parsed_data.json litecoin/pool_addresses.json

zcash: .git
	python3 analyse.py zcash

zcash_clean:
	rm -f zcash/parsed_data.json zcash/pool_addresses.json

tezos: .git
	python3 analyse.py tezos

tezos_clean:
	rm -f tezos/parsed_data.json

clean:
	make bitcoin_clean
	make ethereum_clean
	make bitcoin_cash_clean
	make dogecoin_clean
	make cardano_clean
	make ethereum_classic_clean
	make litecoin_clean
	make zcash_clean
	make tezos_clean
