import requests as r
from bs4 import BeautifulSoup
import csv

base_url = 'https://cardanoscan.io'

pageNo = 1
max_relays = 0
relay_dict = {}

try:
    while True:
        print(f'Scraping page {pageNo}...')
        certificates_url = f'{base_url}/certificates/poolRegistrations?pageNo={pageNo}'
        response_text = r.get(certificates_url).text
        soup = BeautifulSoup(response_text, "html.parser")
        title = soup.find('title')
        if "not found" in title:
            break
        rows = soup.find("table").find("tbody").find_all("tr")

        for row in rows:
            cells = row.find_all("td")

            pool_ticker = cells[2].a['data-tooltip'].split('-')[0].strip()

            tx_ref = cells[0].div.a['href']
            tx_url = f'{base_url}{tx_ref}'
            tx_id = tx_ref.split('?')[0].split('/')[-1]

            tx_response_text = r.get(tx_url).text
            soup2 = BeautifulSoup(tx_response_text, "html.parser")
            relays = soup2\
                .find("div", id="poolcertificates")\
                .find("span", string="Relays").parent\
                .find("div")\
                .find_all("div", recursive=False)
            if len(relays) > max_relays:
                max_relays = len(relays)
            relay_dict[tx_id] = [pool_ticker]
            for relay in relays:
                relay_info = relay.get_text(separator=' ').split()
                relay_ip = relay_info[1]
                relay_dict[tx_id].append(relay_ip)
        pageNo += 1
except Exception as e:
    print(f'The following exception occured: {e}')
finally:
    filename = "cardano_relays2.csv"

    header = ['Transaction id', 'Pool ticker']
    header.extend([f'Relay {i + 1}' for i in range(max_relays)])
    rows = [header]

    for tx_id, val in relay_dict.items():
        row = [tx_id]
        row.extend(list(val))
        rows.append(row)
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
