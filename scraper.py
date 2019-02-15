from bs4 import BeautifulSoup
import urllib.request
import csv

url = 'http://www.fasttrack.co.uk/league-tables/tech-track-100/league-table/'

def main():
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    print(soup)
    table = soup.find('table', attrs={'class': 'tableSorter'})
    results = table.find_all('tr')
    print('Number of results', len(results))
    rows = []
    rows.append(['Rank', 'Company Name', 'Webpage', 'Description', 'Location', 'Year end', 'Annual sales rise over 3 years', 'Sales £000s', 'Staff', 'Comments'])
    print(rows)
    for result in results:
        data = result.find_all('td')
        if len(data) == 0:
            continue
        rank = data[0].getText()
        company = data[1].getText()
        location = data[2].getText()
        yearend = data[3].getText()
        salesrise = data[4].getText()
        sales = data[5].getText()
        staff = data[6].getText()
        comments = data[7].getText()
        company_name = data[1].find('span', attrs={'class':'company-name'}).getText()
        description = company.replace(company_name,'')
        sales = sales.strip('*').strip('†').replace(',', '')
        company_url = data[1].find('a').get('href')
        page = urllib.request.urlopen(company_url)
        soup = BeautifulSoup(page, 'html.parser')
        try:
            tableRow = soup.find('table').find_all('tr')[-1]
            webpage = tableRow.find('a').get('href')
        except:
            webpage = None
        rows.append([rank, company_name, webpage, description, location, yearend, salesrise, sales, staff, comments])
    print(rows)
    with open('techtrack100.csv', 'w', newline='') as f_output:
        csv_output = csv.writer(f_output)
        csv_output.writerows(rows)

main()
