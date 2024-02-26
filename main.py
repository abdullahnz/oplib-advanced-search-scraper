#!/usr/bin/env python3

from oplib import OpenLibrary, AdvancedSearchType

if __name__ == "__main__":
    oplib = OpenLibrary()

    # TODO: Change the search options based on your needs
    search_options = {
        'search[type]': AdvancedSearchType.SKRIPSI,
        'search[number]': '',
        'search[title]': '',
        'search[author]': '',
        'search[publisher]': '',
        'search[editor]': '',
        'search[subject]': '',
        'search[classification]': '',
        'search[location]': '',
        'search[entrance][from][day]': 1,
        'search[entrance][from][month]': 2,
        'search[entrance][from][year]': 2024,
        'search[entrance][to][day]': 31,
        'search[entrance][to][month]': 2,
        'search[entrance][to][year]': 2024,
    }

    content = oplib.get_all_data_from_range_date(**search_options)
    results = oplib.parse_results(content)
    
    for index, totals, data in results:
        print(f"[{index}/{totals}]: {data['title']}")