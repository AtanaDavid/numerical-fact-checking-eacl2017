import numpy as np
import csv
import re

from stanford.corenlpy import Annotation, SharedNERPipeline, CoreAnnotations, number_ne_types, NumberNormalizer


def transpose(l):
    return list(map(list, zip(*l)))

def read_table(filename,base="data/WikiTableQuestions"):
    header = []
    rows = []

    header_read = False
    filename = filename.replace(".csv",".tsv")
    with open(base+"/"+filename,"r") as table:
        has_header = csv.Sniffer().has_header(table.readline())
        table.seek(0)

        for line in csv.reader(table, delimiter="\t"):
            if has_header and not header_read:
                header = line
                header_read = True
            else:
                rows.append(line)
    return {"header": header, "rows":rows}


def number_tuples(table):
    header = table['header']
    rows = table['rows']

    text = ". ".join(" ".join(cell for cell in row) for row in transpose(rows))

    doc = Annotation(text)
    SharedNERPipeline().getInstance().annotate(doc)

    ne_columns = []
    number_columns = []
    for column in range(doc.get(CoreAnnotations.SentencesAnnotation).size()):
        col = doc.get(CoreAnnotations.SentencesAnnotation).get(column)


        tokens = []
        col_ne_tags = []
        for i in range(col.get(CoreAnnotations.TokensAnnotation).size()):
            corelabel = col.get(CoreAnnotations.TokensAnnotation).get(i)
            tokens.append(corelabel.get(CoreAnnotations.TextAnnotation))
            col_ne_tags.append(corelabel.get(CoreAnnotations.NamedEntityTagAnnotation))

        tags = col_ne_tags


        count_in = 0
        if column not in ne_columns:
            for tag in tags:
                if tag in number_ne_types:
                    count_in += 1

            if count_in >= len(tags)/2:
                number_columns.append(column)

    numbers = []


    tuples = []
    transposed = transpose(rows)
    for column in range(len(transposed)):
        for ncolumn in range(len(transposed)):
            if ncolumn in number_columns:
                tuples.extend(list(zip([header[ncolumn]] * len(rows),transposed[column],transposed[ncolumn])))

    return tuples



def number_entity_tuples(table):
    header = table['header']
    rows = table['rows']

    text = ". ".join(" ".join(cell for cell in row) for row in transpose(rows))

    doc = Annotation(text)
    SharedNERPipeline().getInstance().annotate(doc)

    ne_columns = []
    number_columns = []
    for column in range(doc.get(CoreAnnotations.SentencesAnnotation).size()):
        col = doc.get(CoreAnnotations.SentencesAnnotation).get(column)


        tokens = []
        col_ne_tags = []
        for i in range(col.get(CoreAnnotations.TokensAnnotation).size()):
            corelabel = col.get(CoreAnnotations.TokensAnnotation).get(i)
            tokens.append(corelabel.get(CoreAnnotations.TextAnnotation))
            col_ne_tags.append(corelabel.get(CoreAnnotations.NamedEntityTagAnnotation))

        tags = col_ne_tags


        for tag in tags:
            if len(set(col_ne_tags).intersection(set(number_ne_types))) == 0 and tag not in ['NUMBER','NUMERIC','YEAR','DATE','DURATION','TIME','NUMBER','ORDINAL'] and tag != "O":
                ne_columns.append(column)
                break


        count_in = 0
        if column not in ne_columns:
            for tag in tags:
                if tag in number_ne_types:
                    count_in += 1

            if count_in >= len(tags)/2:
                number_columns.append(column)

    numbers = []


    tuples = []
    transposed = transpose(rows)
    for column in range(len(transposed)):
        if column in ne_columns:
            for ncolumn in range(len(transposed)):
                if ncolumn in number_columns:
                    tuples.extend(list(zip([header[ncolumn]] * len(rows),transposed[column],transposed[ncolumn])))

    return tuples