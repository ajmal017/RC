import xml.etree.ElementTree as ET


def read_xml():
    key_financials = {}

    old_new_keys = {
        'PEEXCLXOR': 'PE',
        'MKTCAP': 'MarketCap',
        'NHGH': '12m High'
    }

    tree = ET.parse('./Outputs/ibf_AAPL_ReportSnapshot.xml')
    root = tree.getroot()
    key_financials['Report Name'] = root.tag

    # Get ticker
    for issue_id in root.iter('IssueID'):
        if issue_id.get('Type') == 'Ticker':
            key_financials['ticker'] = issue_id.text

    for ratio in root.iter('Ratio'):
        field_name = ratio.get('FieldName')
        if field_name in old_new_keys.keys():
            key_financials[field_name] = ratio.text

    for k, v in key_financials.items():
        print(k, v)


if __name__ == '__main__':
    read_xml()