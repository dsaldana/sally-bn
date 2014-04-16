from lib_sallybn import util
from libpgm.discretebayesiannetwork import DiscreteBayesianNetwork

DEFAULT_STATES = ["true", "false"]


class DiscreteBayesianNetworkExt(DiscreteBayesianNetwork):
    def __init__(self):

        # Create a clean graph
        self.E = []
        self.V = []
        self.Vdata = {}
        # super(DiscreteBayesianNetworkExt, self).__init__(skel, nd)


    def get_edges(self):
        return self.E

    def get_states(self, vertex_name):
        return self.Vdata[vertex_name]["vals"]

    def set_cprob(self, vertex_name, cprob):
        self.Vdata[vertex_name]["cprob"] = cprob

    def get_cprob(self, vertex_name):

        vertex_cprob = self.Vdata[vertex_name]["cprob"]
        return vertex_cprob

    def get_parent_states(self, vertex_name):

        parents = self.getparents(vertex_name)

        parents_matrix = []
        for par in parents:
            p_sts = self.get_states(par)

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

    def str_parent_states(self, parents_matrix):
        str_pstates = []
        for states in parents_matrix:
            tmp = util.statelist_to_string(states)
            str_pstates.append(tmp)

        return str_pstates


    def add_vertex(self, name):
        # new vertex
        self.V.append(name)

        # Vertex data
        vdata = {}
        vdata["vals"] = list(DEFAULT_STATES)
        vdata["numoutcomes"] = 2
        vdata["cprob"] = [.0, .0]
        vdata["parents"] = []  # just based in libpgm model. but normally None
        vdata["children"] = []  # just based in libpgm model
        vdata["ord"] = 0  # just based in libpgm model

        # Add to dict
        self.Vdata[name] = vdata

        # TODO 2 validate unique name

    def remove_vertex(self, name):
        pass  #todo

    def add_state(self, vertex_name):
        pass  #todo

    def change_state_name(self, vertex_name, old_name, new_name):
        pass  #todo

    def change_vertex_name(self, old_name, new_name):
        # change in edges
        for i in range(len(self.E)):
            # change in parents
            if old_name == self.E[i][0]:
                self.E[i][0] = new_name

                # in vdata
                pars = self.Vdata[self.E[i][1]]["parents"]
                self.Vdata[self.E[i][1]]["parents"] = \
                    util.change_element_in_list(pars, old_name, new_name)

            # change in children
            elif old_name == self.E[i][1]:
                self.E[i][1] = new_name
                # in vdata
                children = self.Vdata[self.E[i][0]]["children"]
                self.Vdata[self.E[i][0]]["children"] = \
                    util.change_element_in_list(children, old_name, new_name)

        self.Vdata[new_name] = self.Vdata.pop(old_name)
        self.V = util.change_element_in_list(self.V, old_name, new_name)

    def add_edge(self, edge):
        # todo validate if exits in the contrary orientation
        parent, child = edge

        self.E.append(edge)

        # add parent
        self.Vdata[child]["parents"].append(parent)

        # add child
        self.Vdata[parent]["parents"].append(child)

        #  Modify CPT in v
        parents_matrix = self.get_parent_states(child)
        str_parent_matrix = self.str_parent_states(parents_matrix)

        new_cprob = {}
        n_outcomes = len(self.get_states(child))
        for s in str_parent_matrix:
            new_cprob[s] = [0.0] * n_outcomes

        self.Vdata[child]["cprob"] = new_cprob




        # TODO If the cpt already exists
        # TODO Validate if the cpt is well formed

    #  # Use the loaded CPT
    # if self.query_v in self.cpts:
    #     print "rows", self.cpts and len(self.cpts[self.query_v]) == n_rows
    #     print "cols", len(self.cpts[self.query_v][0])
    #     print "cos2", n_state_cols
    # # if the table already exists, if nxm is right
    # if self.query_v in self.cpts and len(self.cpts[self.query_v]) == n_rows and \
    #                 len(self.cpts[self.query_v][0]) == n_state_cols:
    #     self.cpt = self.cpts[self.query_v]
    # ## Create a new CPT
    # else:
    #     print "new cpt"
    #     self.cpt = [["0.0"] * n_state_cols for i in range(n_rows)]

    def remove_edge(self, edge):

        self.E.remove(edge)
        parent, child = edge
        self.E.append(edge)

        # add parent
        self.Vdata[child]["parents"].remove(parent)

        # add child
        self.Vdata[parent]["parents"].remove(child)

        # TODO Modify CPT in v
        parents_matrix = self.get_parent_states(child)
        str_parent_matrix = self.disc_bn.str_parent_states(parents_matrix)

        new_cprob = {}
        n_outcomes = len(self.get_states(child))
        for s in str_parent_matrix:
            new_cprob[s] = [0.0] * n_outcomes

        self.Vdata[child]["cprob"] = new_cprob




