import json
import csv
import os
from etk.etk import ETK
from etk.knowledge_graph.schema import KGSchema
from etk.etk_module import ETKModule
from etk.knowledge_graph.node import URI, BNode, Literal, LiteralType
from etk.knowledge_graph.subject import Subject
from etk.csv_processor import CsvProcessor


class ExampleETKModule(ETKModule):
    """
    Abstract class for extraction module
    """

    def __init__(self, etk):
        ETKModule.__init__(self, etk)

        # Load mapping file, maps full country names to abbrevation codes
        # abbv_file_path = 'resources/ctr_code.json'
        # self.abbv_dict = self.abbv_reader(abbv_file_path)

    def abbv_reader(self, path):
        f = open(path, 'r')
        abbv_dict = json.loads(f.read())
        f.close()
        return abbv_dict

    def process_document(self, doc):
        """
        Add your code for processing the document
        """

        # Bind ontologies
        # doc.kg.bind('', 'http://www.ontologyrepository.com/CommonCoreOntologies/Mid/UnitsOfMeasureOntology/')

        #choose
        data_id = doc.select_segments('data_id')[0].value
        rows = doc.select_segments('data')[0].value

        #create dataset subject
        dataset_subject = Subject(URI(':' + data_id ))

        #add each row as object
        for row in rows:
            #extract data from document objects
            row_id = row['row_id']
            symbol = row['Symbol']

            #re-order date
            original_date = row['Date']
            date_list = original_date.split('/')
            date = date_list[2]+date_list[1]+date_list[0]
            open = row['Open']
            high = row['High']
            low = row['Low']
            close = row['Close']

            #create a row subject first
            row_subject = Subject(URI(':'+ data_id +'-row'+row_id))

            # Then we may add multiple properties to the subject we created
            row_subject.add_property(URI('attribute:symbol'), Literal(symbol))
            row_subject.add_property(URI('attribute:date'), Literal(date, type_=LiteralType.date))
            row_subject.add_property(URI('attribute:open'), Literal(open, type_=LiteralType.decimal))
            row_subject.add_property(URI('attribute:low'), Literal(low, type_=LiteralType.decimal))
            row_subject.add_property(URI('attribute:high'), Literal(high, type_=LiteralType.decimal))
            row_subject.add_property(URI('attribute:close'), Literal(close, type_=LiteralType.decimal))

            #add row_subject to dataset_subject as a object
            dataset_subject.add_property(URI('datamart:row'),row_subject)


            # break

        # add subject to kg
        doc.kg.add_subject(dataset_subject)

        return list()


if __name__ == "__main__":
    kg_schema = KGSchema()
    onto_path = 'resources/preloaded-ontologies'
    ontologies = list()

    # Load ontologies in to kg_schema
    for dirpath, dirnames, filenames in os.walk(onto_path):
        for file in filenames:
            f = open(os.path.join(dirpath, file), 'r', encoding='utf-8')
            if os.path.splitext(file)[1] == '.ttl':
                ontologies.append(os.path.join(dirpath, file))
                onto_str = f.read()
                kg_schema.add_schema(onto_str, 'ttl')
            f.close()

    #read id_list.txt to get all the dataset id
    id_file_path = 'D:/USC/ISI/trading/id_list.txt'
    id_set = []
    with open(id_file_path,'r') as f:
        id_set = f.read().split()


    # Read eath data set
    # Create ETK instance, load json dataset to create documents
    etk = ETK(kg_schema=kg_schema, modules=ExampleETKModule)

    #error_list = []

    dataset_path = "resources/dataset"

    #Load data-sets and handle each data-set
    for dirpath, dirnames, filenames in os.walk(dataset_path):
        for file in filenames:
            dataset_id = os.path.splitext(file)[0]
            file_path = os.path.join(dirpath, file)

            # if not os.path.isfile(file_path):
            #     error_list.append(dataset_id)
            #     continue

            #Read dataset from csv file and convert it into dict
            new_list = []
            with open(file_path, 'r') as f:
                reader = csv.reader(f, delimiter=',')
                fieldset = next(reader)
                inner_keyset = fieldset[1:]
                reader = csv.DictReader(f, fieldnames=fieldset, delimiter=',')
                for row in reader:
                    new_dict = {k: row[k] for k in inner_keyset}
                    new_dict['row_id'] = row['']
                    new_list.append(new_dict)

            sample_input = {"data": new_list, "data_id": dataset_id}

            # Create the document
            doc = etk.create_document(sample_input, doc_id="http://isi.edu/default-ns/projects")

            # Process the document and generate RDF
            docs = etk.process_ems(doc)

            # Generate triples and output as a file. Format can also be ttl or json-ld, etc.
            f = open('output/output_' + dataset_id + '.ttl', 'w')
            f.write(docs[0].kg.serialize('ttl'))
            f.close()

    # f1 = open("error_list.txt", "w")
    # for error_id in error_list:
    #     f1.write(error_id+" ")
    # f1.close()

