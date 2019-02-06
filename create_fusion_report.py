from __future__ import print_function
import os
import json

from igv_reports import data_uri

QUOTES = {"'", '"'}
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))


def create_fusion_report(template, table_json):

    basedir = os.path.dirname(template)
    data_uris = {}

    with open(template, "r") as f:
        data = f.readlines()


    for i, line in enumerate(data):
        j = line.find('<!-- start igv report here -->')
        if j >= 0:
            space = ' ' * j
            report_start = i + 1
            break

    else:
        print("file must contain the line \"<!-- start igv report here -->\"")
        return


    input_lines = data[report_start:]
    output_lines = []


    #insert json for selection table
    with open(table_json, "r") as f:
        j = json.loads(f.read())
        flattend_json = json.dumps(j)

    output_lines.append('var tableJson = ' + flattend_json)


    for line_index, line in enumerate(input_lines):

        is_index = line.find('indexURL:') > 0
        if is_index:
            continue

        i = line.lower().find('url:')

        if i >= 0:
            i += 4
            while line[i] not in QUOTES and i < len(line):
                i += 1
            i += 1
            start = i
            while line[i] not in QUOTES and i < len(line):
                i += 1
            filename = line[start:i]
            output_lines.append(line[:start - 1] + 'data["' + filename + '"]' + line[i+1:])
            if os.path.exists(os.path.join(basedir, filename)):
                data_uris[filename] = data_uri.file_to_data_uri(os.path.join(basedir, filename))


        else:
            output_lines.append(line)

    report_header =  data[:report_start]

    report_data_uris = create_data_var(data_uris, space)

    report_body = output_lines

    new_html_data = report_header + report_data_uris + report_body

    output_name = os.path.join(template[:-5] + '_report' + template[-5:])
    with open(output_name, 'w') as f:
        f.writelines(new_html_data)


def create_data_var(data_uris, space=''):
    data = []
    for i, (key, value) in enumerate(data_uris.items()):
        data.append('{}"{}": "{}"{}\n'.format(space + ' ' * 4, key, value, ',' if i < len(data_uris) - 1 else ''))
    return [space + "var data = {\n"] + data + [space+"};\n"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the html file to be converted")
    parser.add_argument("tableJson", help="json file encoding the selection table")
    args = parser.parse_args()

    create_fusion_report(args.filename, args.tableJson)
