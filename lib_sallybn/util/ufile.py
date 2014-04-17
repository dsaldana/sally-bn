import json


def dic_from_json_file(file_name):
    f = open(file_name, 'r')
    json_file = f.read()
    assert (json_file and isinstance(json_file, str)), "Input file is empty or could not be read."

    # alter for json input, if necessary
    json_data = None
    try:
        json_data = json.loads(json_file)
    except ValueError:
        pass

    if json_data is None:
        try:
            json_file = json_file.translate(None, '\t\n ')
            json_file = json_file.replace(':', ': ')
            json_file = json_file.replace(',', ', ')
            json_file = json_file.replace('None', 'null')
            json_file = json_file.replace('.', '0.')
            json_data = json.loads(json_file)

            return json_data
        except ValueError:
            raise ValueError, "Convert to JSON from input file failed. Check formatting."
    f.close()

def dic_to_file(dic, file_name):

    with open(file_name, 'w') as outfile:
        json.dump(dic, outfile)