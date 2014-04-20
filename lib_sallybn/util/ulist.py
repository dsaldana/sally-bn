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

def statelist_to_string(states):
    tmp = "["
    for i in range(len(states)):
        tmp += "'" + states[i] + "'"

        # put comma if it is not the last one
        if i < len(states) - 1:
            tmp += ", "
    tmp += "]"
    return tmp



def change_element_in_list(old_list, old_name, new_name):
    new_list = []
    for p in old_list:
        if p == old_name:
            new_list.append(new_name)
        else:
            new_list.append(p)
    return new_list


def list_to_str_list(list):
    res = [str(a) for a in list]
    return res