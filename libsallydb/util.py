


def parent_states(parents, states):
    """

    :param parents: list of parent names
    :param states: disctionary with k=vertex names and v=list of states
    """
    parents_matrix = []
    for par in parents:
        p_sts = states[par]

        if not parents_matrix:
            parents_matrix = [[s] for s in p_sts]
        else:
            new_par_matrix = []
            # previous parents
            for prev_p in parents_matrix:
                for pstate in p_sts:
                    tmp = list(prev_p)
                    tmp.append(pstate)
                    new_par_matrix.append(tmp)

            parents_matrix = new_par_matrix
    return parents_matrix


def get_parents(vertex, edges):
    """
    get the parents for a vertex in a list of edges
    :param vertex:
    :param edges:
    :return:
    """
    parents = []
    for v1, v2 in edges:
        if v2 == vertex:
            parents.append(v1)
    return parents