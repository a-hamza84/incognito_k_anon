from dgh import CsvTable
from vertex import Vertex
from edge import Edge
from graph import Graph
from copy import deepcopy
from mergesort import MergeSort
import pandas as pd
import numpy as n


class Incognito:
    def __init__(self, csv_path):
        """Initialize Algorithm

        Args:
            csv_path (str): path to csv containing data to anonimize
        """
        self.combinations_list = []
        self.main_graph = None
        self.k_anon_combinations = []
        self.checker = []
        self.quasi_iden = ['state', 'date_year', 'age', 'race', 'flee']
        self.checker_quasi = []
        self.r_attribute_gen = {}
        self.dgh_paths = {}
        header = './HC'
        for item in self.quasi_iden:
            self.dgh_paths[item] = f'{header}/HC_{item}.csv'
        self.csv_dgh = CsvTable(
            csv_path, dgh_paths=self.dgh_paths, dgh_objs=None
        )
        self.dgh_trees = self.csv_dgh.dghs
        self.table = pd.read_csv(csv_path, header=0)
        # transform date death column
        self.table['date'] = pd.to_datetime(
            self.table['date'], format='%m/%d/%Y'
        )
        self.table['date_month'] = self.table['date'].dt.month
        self.table['date_day'] = self.table['date'].dt.day
        self.table['date_year'] = self.table['date'].dt.year
        self.table.drop('date', axis=1, inplace=True)
        # self.table = self.csv_dgh.table.re
        self.path = csv_path

    def main_algorithm(self, kAnon):
        """Main algorithm  as mentioned in research paper

        Args:
            kAnon (int): k value in k-anonimity
        """
        self.generate_quasi_combinations(1)
        self.create_graphs_for_r_attributes()
        queue = []
        total_comb = 0

        for i in range(1, len(self.quasi_iden) + 1):
            for x in range(len(self.combinations_list)):
                total_comb += len(self.combinations_list[x])
                temp_graph = self.r_attribute_gen[self.combinations_list[x]]
                queue = self.sort_by_height(temp_graph.get_roots())
                print(f'quasi iden: {self.quasi_iden[i-1]}')
                print(f'quasi comb: {self.combinations_list[x]}')
                while queue:
                    node = queue.pop(0)
                    issaKnon = False

                    if node.is_marked():
                        print("marked node:", node.get_data())

                    else:
                        issaKnon = self.generalize_with_level(
                            s=node.get_data(), k_anon=kAnon
                        )
                        print("work node:", node.get_data())
                        print("Am I k-Anon?", issaKnon)
                        # print()
                        if issaKnon:
                            self.mark_all_gens(node)
                        else:
                            queue = node.get_direct_generalizations(
                                deepcopy(queue)
                            )
                            # queue.extend(further_gens)
                            queue = self.sort_by_height(queue)

            self.generate_quasi_combinations(i + 1)
            self.create_graphs_for_r_attributes()
        print(f'len org: {total_comb}')
        print(f'len kanon: {len(self.k_anon_combinations)}')

    def view_gen_combinations(self):
        """View all the generated combinations which will produce
        k-anonimous table
        """
        print("Combinations that are k-Anon:")
        for m in range(len(self.k_anon_combinations)):
            print(self.k_anon_combinations[m])

    def print_k_anon_tables(self):
        """print whole k-anonimoud table
        (might not be required, but placed just in case needed)
        """
        print("Generalized Tables that are k-Anon:")
        for i in range(len(self.k_anon_combinations)):
            self.generalize_with_level(s=self.k_anon_combinations[i])

    def generate_quasi_combinations(self, r=None):
        """generate all the possible quasi combinations with len of r

        Args:
            r (int, optional): length of combination list. Defaults to None.
        """
        self.combinations_list = []
        quasiIden = self.quasi_iden

        if r is None:
            r = len(quasiIden)

        self.combination(
            quasiIden, [None] * len(quasiIden), 0, len(quasiIden) - 1, 0, r
        )

    def combination(self, input, temp, start, end, index, r):
        """combination algorithm to genetae quasi combinations

        Args:
            input (list): list of quasi identifiers
            temp (list): temporary list for use
            start (int): start index of input
            end (int): end index of input
            index (int): current index of input
            r (int): length of resulting list
        """
        # Current combination is ready to be added to list
        if index == r:
            combine = temp[0] + " " + str(self.get_DG_height(temp[0]))
            for j in range(1, r):
                combine = (
                    combine
                    + ":"
                    + temp[j]
                    + " "
                    + str(self.get_DG_height(temp[j]))
                )
            self.combinations_list.append(combine)
        # Replace index with all possible elements. The condition
        # "end-i+1 >= r-index" makes sure that including one element
        # at index will make a combination with remaining elements
        # at remaining positions
        for i in range(start, end + 1):
            if end - i + 1 >= r - index:
                temp[index] = input[i]
                self.combination(input, temp, i + 1, end, index + 1, r)

    def get_DG_height(self, quasi):
        """Get DGH tree hieght against this quasi identifier

        Args:
            quasi (str): quasi identifier

        Returns:
            height
        """
        for k, v in self.dgh_trees.items():
            if k.lower() == quasi.lower():
                return str(v.hierarchies['*'].get_height() - 1)
        return ""

    def descend_from_top_vertex(self, v):
        """traverse the graph and add vertex v

        Args:
            v (Vertex): Vertex to add
        """
        arr = v.get_data().split(":")
        quasi_id_top_heights = {}

        for i in range(len(arr)):
            quasi_id = arr[i].split(" ")[0]
            top_height = int(arr[i].split(" ")[1])
            quasi_id_top_heights[quasi_id] = top_height

        quasi_id = list(quasi_id_top_heights.keys())

        for i in range(len(quasi_id)):
            old_value = quasi_id_top_heights[quasi_id[i]]
            new_value = quasi_id_top_heights[quasi_id[i]] - 1

            if new_value >= 0:
                quasi_id_top_heights[quasi_id[i]] = new_value

                possible_vertex = ""

                for j in range(len(quasi_id)):
                    possible_vertex += (
                        quasi_id[j].strip()
                        + " "
                        + str(quasi_id_top_heights[quasi_id[j]])
                        + ":"
                    )

                quasi_id_top_heights[quasi_id[i]] = old_value

                vertex2 = Vertex(possible_vertex[:-1])
                vertex2 = self.main_graph.has_vertex(vertex2)
                edge = Edge(vertex2, v)
                vertex2.add_incident_edge(edge)
                self.main_graph.add_edge_obj(edge)
                self.main_graph.add_vertex(vertex2)

        # main_graph.print_out()

    def check_if_at_bottom(self, v):
        """check of vertex v is at the bottom of the graph

        Args:
            v (Vertex): Vertex to check
        """
        arr = v.get_data().split(":")
        for i in range(len(arr)):
            index = int(arr[i].split(" ")[1])
            if index != 0:
                return False
        return True

    def create_graphs_for_r_attributes(self):
        """create lattice graph for combination list made in previous step"""
        for j in range(len(self.combinations_list)):
            top_root = Vertex(self.combinations_list[j])
            self.main_graph = Graph()
            self.main_graph.add_vertex(top_root)
            orig_length = len(self.main_graph.get_vertices())
            self.descend_from_top_vertex(self.main_graph.get_vertex(0))

            while not self.check_if_at_bottom(
                self.main_graph.get_vertex(orig_length - 1)
            ):
                new_length = len(self.main_graph.get_vertices())

                if new_length > orig_length:
                    for i in range(orig_length, new_length):
                        self.descend_from_top_vertex(
                            self.main_graph.get_vertex(i)
                        )

                orig_length = new_length

            self.r_attribute_gen[
                self.combinations_list[j]
            ] = self.main_graph.copy()

    def sort_by_height(self, queue):
        """sort the queue made during graph traversal by hieght of quasi's DGH

        Args:
            queue (list): list of Vextices of graph

        Returns:
            sorted queue
        """
        ms = MergeSort()
        return ms.sort(queue)

    def add_new_elem(self, item, dgh):
        """get new generalized value using DGH for the item
        Args:
            item (Any): value to generalize
            dgh (DGH): DGH Tree selected

        Returns:
            Generalized value for the item
        """
        if item == n.nan:
            return item
        if isinstance(item, float):
            try:
                item = str(int(item))
            except:
                return n.nan
        else:
            item = str(item)
        new_element = dgh.generalize(item)
        return new_element

    def generate_table_with_dgh_table(
        self, old_table, dgh_tree, column_to_generalize
    ):
        """generate new table with generalized value using specific combination

        Args:
            old_table (pd.dataframe): table to generalize
            dgh_tree (DGH): DGH for a quasi iden
            column_to_generalize (str): column name to generalize

        Returns:
            _type_: _description_
        """
        new_table = deepcopy(old_table)
        new_table[column_to_generalize] = new_table[column_to_generalize].apply(
            self.add_new_elem, dgh=dgh_tree
        )
        return new_table

    def get_table_comb(self, combs):
        """Get a combination which will generate final resulting table as result

        Args:
            combs (list): quasi combinations

        Returns:
            a combination best for result
        """
        for i in reversed(range(1, len(self.quasi_iden) + 1)):
            for comb in combs:
                count = 0
                arr = comb.split(':')
                if len(arr) < i:
                    continue
                for item in arr:
                    if int(item.split(' ')[1]) != 0:
                        count += 1
                if count == len(arr):
                    print(f'Combination selected: {comb}')
                    return comb
        return None

    def return_kanon_table(self):
        """generate final table which k-anonimous"""
        print("Generalized Table that is k-Anon:")
        kanon_comb = self.get_table_comb(self.k_anon_combinations)
        self.generalize_with_level(s=kanon_comb)

    def generalize_with_level(self, s, k_anon=None):
        """Keep generating generalized tables until we have
           combination with k-anonimous table

        Args:
            s (string): quasi combination to check
            k_anon (int, optional): value of k. Defaults to None.
        """
        new_table = deepcopy(self.table)
        # new_table.to_csv('temp.csv')
        # new_dgh = CsvTable('temp.csv', dgh_paths=None, dgh_objs=self.dgh_trees)
        new_dgh = self.csv_dgh
        new_dgh = new_dgh.dghs
        arr = s.split(":")
        index = -1
        t_tree = None
        self.checker_quasi = []
        self.checker_quasi = [item.split(' ')[0] for item in arr]
        for i in range(len(arr)):
            for j, (k, v) in enumerate(new_dgh.items()):
                if k == arr[i][: arr[i].index(" ")]:
                    index = list(new_table.columns).index(k)
                    t_tree = v
                    col_work = k

            generalization_level = int(arr[i][arr[i].index(" ") + 1 :])
            # generalization_level = t_tree.gen_levels['*']-1
            x = 0

            while x < generalization_level:
                new_table = self.generate_table_with_dgh_table(
                    new_table, t_tree, col_work
                )
                if index not in self.checker:
                    self.checker.append(index)
                x += 1

        if k_anon is not None:
            return self.check_table(k_anon, new_table)
        new_table.to_csv('result.csv')
        # print(new_table)

    def mark_all_gens(self, v):
        """mark vertex edges for k-anonimity true

        Args:
            v (Vertex): Vertex to mark
        """
        self.addListOfGeneralizations(v)
        for edge in v.get_incident_edges():
            self.mark_all_gens(edge.get_to())

    def addListOfGeneralizations(self, node):
        """mark a specific node in the graph for k-anonimity

        Args:
            node (Node): Node of r_attribute graph
        """
        node.set_mark(True)
        if node.get_data() not in self.k_anon_combinations:
            self.k_anon_combinations.append(node.get_data())

    def get_quasi_col_num(self, table):
        """
        Column numbers of selected quasi identifiers
        """
        quasi_col_num = []
        for quasi in self.checker_quasi:
            quasi_col_num.append(list(table.columns).index(quasi))
        return quasi_col_num

    def get_freq_set(self, table):
        """
        Get frequency set for all the combinations from table
        """
        quasi_col_num = self.get_quasi_col_num(table)
        freq_set = {}
        i = 0
        while i < len(table):
            quasi_iden = []
            for x in quasi_col_num:
                quasi_iden.append(table.iat[i, x])
            quasi_iden = tuple(quasi_iden)
            if quasi_iden in freq_set:
                freq_set[quasi_iden] += 1
            else:
                freq_set[quasi_iden] = 1
            i += 1
        return freq_set

    def check_table(self, kanon, table):
        """
        To check k anonimity of the table generated
        """
        freq_set = self.get_freq_set(table)
        for k, v in freq_set.items():
            if n.nan in k:
                continue
            if v < kanon:
                return False
        return True


import time

start_time = time.time()
incog = Incognito('temp_data.csv')
incog.main_algorithm(2)

# displaying generalizations
incog.view_gen_combinations()
incog.checker = []
incog.return_kanon_table()

print(incog.checker)
print((time.time() - start_time) / 60)
