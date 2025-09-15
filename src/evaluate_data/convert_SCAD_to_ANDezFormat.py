from src.create_data.useful_functions import original_data_path,dumpFolder_path

from sklearn.model_selection import train_test_split
import xmltodict
import csv
import re

# extracts all authors from a publication along with their ids.
# authors_obj: the authos of a publication
# returns authors_parsed: the authors in a list
# returns ids_parsed: the ground truth ids as a list
def process_authors(authors_obj):
    authors = authors_obj.get("author", [])
    if not isinstance(authors, list):
        authors = [authors]
    authors_parsed = []
    ids_parsed = []
    for a in authors:
        name = a.get("@name", "")
        name = name.strip().lower()
        name = re.sub(r'\.', ' ', name)
        name = re.sub(r'\s+', ' ', name)

        authors_parsed.append(name)
        ids_parsed.append(a.get("@id", ""))

    return authors_parsed, ids_parsed


# prints the ANDez files into the required format
# record_mode: either "w" for write or "a" for add. With this you choose if you want to add to the record file or if you want to start a new file.
# record_path: the name of the "records" file required by ANDez
# signatures_path: the name of the "signatures" file required by ANDez
# clusters_path: the name of the "clusters" file required by ANDez
# publications: the xml data that should go into these files
# paper_id: the paper id with which to start counting
# instance_id: the instance id with which to start counting
# cluster_id: the cluster id with which to start counting
# Returns the paper, instance and cluster id that starting with the lowest unused value. This is to ensure no overlap of ids.
def print_to_txt(record_mode,record_path,signatures_path,clusters_path,publications,paper_id,instance_id,cluster_id):
    cluster_dict = {}
    with open(record_path, record_mode, encoding='utf-8', newline='') as record_out,\
          open(signatures_path, 'w', encoding='utf-8', newline='') as signatures_out,\
          open(clusters_path, 'w', encoding='utf-8', newline='') as clusters_out:
        record_writer = csv.writer(record_out, delimiter='\t')
        signatures_writer = csv.writer(signatures_out, delimiter='\t')
        clusters_writer = csv.writer(clusters_out, delimiter='\t')

        for pub in publications:
            authors_data = pub.get("authors", {})
            authors, author_ids = process_authors(authors_data)
            if authors == ["v"]:
                continue
            venue = pub.get("venue")
            year = pub.get("year")
            title = pub.get("title")
            record_writer.writerow([
                paper_id,
                year,
                venue,
                "|".join(authors),
                title
            ])
            for index,a in enumerate(authors,start=1):
                name_split = re.split(r'[,\s\-]+', a.strip())
                last = name_split[0].lower()
                first_initial = name_split[1][0].lower()
                signatures_writer.writerow([
                    instance_id,
                    paper_id,
                    index,
                    a,
                    "",
                    f"{last}_{first_initial}"
                ])
                a_id = author_ids[index-1]
                if a_id in cluster_dict.keys():
                    cluster_dict[a_id].append(str(instance_id))
                else:
                    cluster_dict[a_id] = [str(instance_id)]
                instance_id += 1
            paper_id+=1
        for cluster in cluster_dict.keys():
            clusters_writer.writerow([
                cluster_id,
                "|".join(cluster_dict[cluster])
                ])
            cluster_id += 1
    return paper_id,instance_id,cluster_id


# Splits the SCAD-zbMath xml into two equal halves and saves them.
# It also converts those train and test xml into the format required by ANDez and saves all necessary files.
# xml_path: the current location of the xml
# record_path: the name of the "records" file required by ANDez
# signatures_path: the name of the "signatures" file required by ANDez
# clusters_path: the name of the "clusters" file required by ANDez
def xml_to_tsv(xml_path, record_path, signatures_path,clusters_path):
    paper_id = 1
    instance_id = 1
    cluster_id = 1
    with open(xml_path, 'r', encoding='utf-8') as f:
        data = xmltodict.parse(f.read())
    publications = data['publications']['publication']
    pub_train, pub_test = train_test_split(publications, test_size=0.5, random_state=42)
    save_xml(pub_train, dumpFolder_path() + "/scad_train.xml")
    save_xml(pub_test, dumpFolder_path()+"/scad_test.xml")
    paper_id,instance_id,cluster_id = print_to_txt('w',record_path+".txt",signatures_path+"_train.txt",clusters_path+"_train.txt",pub_train,paper_id,instance_id,cluster_id)
    print_to_txt('a',record_path+".txt",signatures_path+"_test.txt",clusters_path+"_test.txt",pub_test,paper_id,instance_id,cluster_id)


# Saves the xml
# pub_list: the publications (already in xml) to save
# filename: the path and name where to save the xml
def save_xml(pub_list, filename):
    wrapped = {'publications': {'publication': pub_list}}
    xml_str = xmltodict.unparse(wrapped, pretty=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_str)


# Running this script converts the SCAD-zbMath dataset from xml into the format required by ANDez.
# It also splits the xml into a train and test split so that the same split can be used for ANDez and other solutions.
if __name__ == '__main__':
    xml_to_tsv(dumpFolder_path()+"/scad-zbmath-01-open-access.xml",dumpFolder_path()+"/records",dumpFolder_path()+"/signatures",dumpFolder_path()+"/clusters")