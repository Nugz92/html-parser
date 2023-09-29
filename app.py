import csv
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    if table is None:
        return None, None, None

    order_numbers, started_production_dates, values = [], [], []

    header_row = table.find('tr')
    headers = [header.text.strip() for header in header_row.find_all('th')]

    order_number_index = headers.index('Order Number')
    started_production_index = headers.index('Started Production')
    value_index = headers.index('Value')

    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')

        if len(columns) > max(order_number_index, started_production_index, value_index):
            order_numbers.append(columns[order_number_index].text.strip())
            started_production_dates.append(columns[started_production_index].text.strip())
            values.append(columns[value_index].text.strip())

    return order_numbers, started_production_dates, values

def write_to_csv(order_numbers, started_production_dates, values, csv_file):
    rows = zip(order_numbers, started_production_dates, values)

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Order Number', 'Started Production', 'Value'])
        writer.writerows(rows)

@app.route('/parse-email', methods=['POST'])
def parse_email():
    try:
        html_content = request.data.decode('utf-8')
        order_numbers, started_production_dates, values = extract_data(html_content)

        if order_numbers is None:
            return jsonify({'error': 'No table found in the HTML'}), 400

        csv_file = '/app/output.csv'
        write_to_csv(order_numbers, started_production_dates, values, csv_file)
        return jsonify({'message': 'CSV file generated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
