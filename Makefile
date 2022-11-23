ALL:

bitcoin: .git
	python3 execute.py bitcoin

bitcoin_clean:
	rm -f ledgers/bitcoin/parsed_data.json ledgers/bitcoin/pool_addresses.json

ethereum: .git
	python3 execute.py ethereum

ethereum_clean:
	rm -f ledgers/ethereum/parsed_data.json ledgers/ethereum/pool_addresses.json

bitcoin_cash: .git
	python3 execute.py bitcoin_cash

bitcoin_cash_clean:
	rm -f ledgers/bitcoin_cash/parsed_data.json ledgers/bitcoin_cash/pool_addresses.json

dogecoin: .git
	python3 execute.py dogecoin

dogecoin_clean:
	rm -f ledgers/dogecoin/parsed_data.json ledgers/dogecoin/pool_addresses.json

cardano: .git
	python3 execute.py cardano

cardano_clean:
	rm -f ledgers/cardano/parsed_data.json

ethereum_classic: .git
	python3 execute.py ethereum_classic

ethereum_classic_clean:
	rm -f ledgers/ethereum_classic/parsed_data.json ledgers/ethereum_classic/pool_addresses.json

litecoin: .git
	python3 execute.py litecoin

litecoin_clean:
	rm -f ledgers/litecoin/parsed_data.json

zcash: .git
	python3 execute.py zcash

zcash_clean:
	rm -f ledgers/zcash/parsed_data.json ledgers/zcash/pool_addresses.json

tezos: .git
	python3 execute.py tezos

tezos_clean:
	rm -f ledgers/tezos/parsed_data.json

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
