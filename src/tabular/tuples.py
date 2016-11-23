import re

from distant_supervision.query_generation import normalise
from tabular.table_collection import TableCollection
from tabular.table_reader import number_entity_tuples, number_tuples


def get_all_tuples(tables,query):
    a = tables.get_tables_for_word(query)
    results = set()
    results.update(a["exact"])
    results.update(a["partial"])

    print("Found "+ str(len(results)) + " possible candidate tables")

    all_tuples = []
    for result in results:
        new_result = dict()
        table_name = result
        result = TableCollection.instance().load(result)

        new_result['header'] = result['header']
        new_result['rows'] = []

        matched = False
        for row in result['rows']:
            match = False

            for cell in row:
                if not set(normalise(cell).split()).isdisjoint(normalise(query).split()):
                    match = True
                    break

            if match:
                matched = True
                new_result['rows'].append(row)

        if matched:
            tuples = number_tuples(new_result)
            if len(tuples) > 0:
                for tuple in tuples:
                    all_tuples.append((table_name,tuple))
    return filter_tuples_for_entity(all_tuples,query)



def filter_tuples_for_entity(tuples,query):
    ret = []
    for tuple in tuples:
        if set(normalise(tuple[1][1]).split()).intersection(set(normalise(re.sub(r"[^A-Za-z\s]+","",query)).split())):
            ret.append(tuple)
    return ret