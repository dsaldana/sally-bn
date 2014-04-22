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

import copy
from lib_sallybn.util import ulist
from libpgm.discretebayesiannetwork import DiscreteBayesianNetwork
from libpgm.tablecpdfactorization import TableCPDFactorization

DEFAULT_STATES = ["true", "false"]


class DiscreteBayesianNetworkExt(DiscreteBayesianNetwork):
    def __init__(self, skel=None, nd=None):
        if skel is None and nd is None:
            # Create a clean graph
            self.E = []
            self.V = []
            self.Vdata = {}
        else:
            super(DiscreteBayesianNetworkExt, self).__init__(skel, nd)

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
            tmp = ulist.statelist_to_string(states)
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

    def remove_vertex(self, vertex_name):
        # delete edges
        for [v1, v2] in self.E:
            if v1 == vertex_name or v2 == vertex_name:
                self.remove_edge([v1, v2])

        # Vertex
        self.V.remove(vertex_name)

    def add_state(self, vertex_name, new_state):
        ## Outcomes
        n_outcomes = len(self.get_states(vertex_name)) + 1
        self.Vdata[vertex_name]["numoutcomes"] = n_outcomes

        ## states (vals)
        self.Vdata[vertex_name]["vals"].append(new_state)

        ## cprob
        parents_matrix = self.get_parent_states(vertex_name)
        str_parent_matrix = self.str_parent_states(parents_matrix)

        new_cprob = {}
        for s in str_parent_matrix:
            new_cprob[s] = [0.0] * n_outcomes

        # if no parents
        if not parents_matrix:
            new_cprob = [0.0] * n_outcomes

        self.Vdata[vertex_name]["cprob"] = new_cprob

        # For children
        children = self.getchildren(vertex_name)

        for child in children:
            #  Modify CPT in v
            parents_matrix = self.get_parent_states(child)
            str_parent_matrix = self.str_parent_states(parents_matrix)

            new_cprob = {}
            n_outcomes = len(self.get_states(child))
            for s in str_parent_matrix:
                new_cprob[s] = [0.0] * n_outcomes

            self.Vdata[child]["cprob"] = new_cprob

    def change_state_name(self, vertex_name, old_name, new_name):
        # state name
        l_vals = self.Vdata[vertex_name]["vals"]
        self.Vdata[vertex_name]["vals"] = \
            ulist.change_element_in_list(l_vals, old_name, new_name)

        # CPT in children
        children = self.getchildren(vertex_name)
        for child in children:
            cprob = self.Vdata[child]["cprob"]

            cpt = [cprob[k] for k in cprob.keys()]
            parents_mtx = self.get_parent_states(child)
            str_parent_mtx = self.str_parent_states(parents_mtx)

            new_cprob = {}
            # Maybe this is not the best way
            for j in range(len(str_parent_mtx)):
                new_cprob[str_parent_mtx[j]] = cpt[j]

            self.Vdata[child]["cprob"] = new_cprob


    def change_vertex_name(self, old_name, new_name):
        # change in edges
        for i in range(len(self.E)):
            # change in parents
            if old_name == self.E[i][0]:
                self.E[i][0] = new_name

                # in vdata
                pars = self.Vdata[self.E[i][1]]["parents"]
                self.Vdata[self.E[i][1]]["parents"] = \
                    ulist.change_element_in_list(pars, old_name, new_name)

            # change in children
            elif old_name == self.E[i][1]:
                self.E[i][1] = new_name
                # in vdata
                children = self.Vdata[self.E[i][0]]["children"]
                self.Vdata[self.E[i][0]]["children"] = \
                    ulist.change_element_in_list(children, old_name, new_name)

        self.Vdata[new_name] = self.Vdata.pop(old_name)
        self.V = ulist.change_element_in_list(self.V, old_name, new_name)

    def add_edge(self, edge):
        parent, child = edge

        # validate if exits in the contrary orientation
        if [child, parent] in self.E:
            return
        elif edge in self.E:
            return

        self.E.append(edge)

        # add parent
        self.Vdata[child]["parents"].append(parent)

        # add child
        self.Vdata[parent]["children"].append(child)

        #  Modify CPT in v
        self.create_new_cprob(child)

    def remove_edge(self, edge):
        parent, child = edge

        # Remove edge
        self.E.remove(edge)

        # remove parent's Vdata for child
        self.Vdata[child]["parents"].remove(parent)
        # new cprob for child
        self.create_new_cprob(child)

        # remove children's Vdata for parent
        self.Vdata[parent]["children"].remove(child)
        # new cprob for parent
        self.create_new_cprob(parent)

    def get_vertices(self):
        return self.V

    def get_vdata(self):
        return self.Vdata

    def create_new_cprob(self, vertex):
        parents_matrix = self.get_parent_states(vertex)
        str_parent_matrix = self.str_parent_states(parents_matrix)

        new_cprob = {}
        n_outcomes = len(self.get_states(vertex))

        if str_parent_matrix:
            for s in str_parent_matrix:
                new_cprob[s] = [0.0] * n_outcomes
        else:
            new_cprob = [0.0] * n_outcomes

        self.Vdata[vertex]["cprob"] = new_cprob

    def validate_cprob(self, vertex_name):
        cprob = self.Vdata[vertex_name]["cprob"]

        # no parents
        if not self.getparents(vertex_name):
            if 1 - sum(cprob) > 0.001:
                return False
            else:
                return True
        # Has parents
        for k, v in cprob.iteritems():
            # must sum 1
            if 1 - sum(v) > 0.001:
                return False
        return True

    def clone(self):
        clone = DiscreteBayesianNetworkExt()
        clone.E = list(self.E)
        clone.V = list(self.V)
        clone.Vdata = copy.deepcopy(self.Vdata)
        return clone

    def compute_marginals(self, evidence={}):
        """ Compute the marginal probabilities for each node

        :return: a dictionary with: vertexname -> state name -> marginal values
            ex. {"v1":{"state1": 0.5, "state2": 0.5}}
        """
        marginals = {}
        for v in self.V:

            query = {v: ''}

            vertex_marginals = {}
            states = self.get_states(v)

            ## if evidence node
            if v in evidence:
                vals = []
                s_evidence = evidence[v]
                for s in states:
                    if s == s_evidence:
                        vertex_marginals[s] = 1.0
                    else:
                        vertex_marginals[s] = 0.0
            # if query node.
            else:
                #marginal values
                fn = TableCPDFactorization(self.clone())
                mar_vals = fn.condprobve(query, evidence)

                # Associate marginals with values
                for i in range(len(states)):
                    vertex_marginals[states[i]] = mar_vals.vals[i]

            marginals[v] = vertex_marginals

        return marginals

