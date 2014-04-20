# ----------------------------------------------------------------------------
#
# Sally BN: An Open-Source Framework for Bayesian Networks.
#
# ----------------------------------------------------------------------------
# GNU General Public License v2
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ----------------------------------------------------------------------------

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

            json_data
        except ValueError:
            raise ValueError, "Convert to JSON from input file failed. Check formatting."
    return json_data
    f.close()

def dic_to_file(dic, file_name):

    with open(file_name, 'w') as outfile:
        json.dump(dic, outfile)