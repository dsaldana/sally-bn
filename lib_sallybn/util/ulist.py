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