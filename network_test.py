import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import time
import csv

import csv_test

REGULAR_NODE = 0
RELAY_NODE = 1

ADV_TIME = 25

MSG_PAYLOAD_SIZE = 11

class MeshNode(object):
	# 4.2.2.7 Publish Retransmit Interval Steps: Minimum 50ms
	# 4.2.19.2 Network Transmit Interval Steps: Minimum random 0-10ms
	# 4.2.20.2 Relay Retransmit Interval Steps: Minimum 10ms

	# Mulig Network Transmit Interval og Relay Retransmit Interval kan nulles ut siden den ene gjelder GATT og den andre ADV Bearer

	def __init__(self, name, number, packet_loss_chance, retransmit=1):
		self.name = name
		self.number = number
		self.packet_loss_chance = packet_loss_chance

		self.adjecent_nodes = []
		self.msg_cache = []
		self.msg_approved = 0
		self.last_msg_timestamp = 0
		self.retransmit = retransmit

	def start_dfu(self, n_bytes):
		dfu_msg_cnt = math.ceil(n_bytes / MSG_PAYLOAD_SIZE)
		timestamp = 0
		start = time.time()
		for i in range(1, dfu_msg_cnt + 1):
			if i % 100 is 0:
				print(i)
			self.add_cache_entry(i)
			self.msg_approved += 1
			if timestamp > self.last_msg_timestamp:
				self.last_msg_timestamp = timestamp
			self.advertise_message(i, timestamp, timestamp)
			timestamp += 75
		print("Messages sent: {}, Time expired: {}".format(dfu_msg_cnt, timestamp))
		stop = time.time()
		print("Run took: {}".format(stop - start))
		return dfu_msg_cnt

	def advertise_message(self, tid, timestamp, origin_timestamp):
		for i in range(1, self.retransmit + 1):
			for node in self.adjecent_nodes:
				node.start_receive_msg(tid, (timestamp + (ADV_TIME * i)), origin_timestamp)


	def add_neighbour_node(self, node):
		if node not in self.adjecent_nodes:
			self.adjecent_nodes.append(node)
			node.adjecent_nodes.append(self)

	def add_cache_entry(self, entry):
		if len(self.msg_cache) >= 10:
			self.msg_cache.pop(0)

		self.msg_cache.append(entry)

	def start_receive_msg(self, tid, timestamp, origin_timestamp):

		if self.was_msg_recieved(self.packet_loss_chance):

			if tid in self.msg_cache:
				return True
			self.add_cache_entry(tid)
			self.msg_approved += 1
			if timestamp > self.last_msg_timestamp:
				self.last_msg_timestamp = timestamp

			self.advertise_message(tid, timestamp, origin_timestamp)
			return True

		return False

	@staticmethod
	def was_msg_recieved(loss_chance):
		return random.random() > loss_chance/100

	def print_result(self):
		print("{}: Messages successfully received: {}".format(self.name ,self.msg_approved))
		return [self.name, self.last_msg_timestamp, self.msg_approved]


class MeshNetwork(object):

	def __init__(self, node_cnt, packet_loss_chance, retransmit=1):
		self.node_cnt = node_cnt
		self.packet_loss_chance = packet_loss_chance
		self.retransmit = retransmit

		self.g = nx.barabasi_albert_graph(node_cnt, 2)
		self.nodes_dict = {}
		self.create_network()
		self.create_edges()
		self.test_res = csv_test.TestResults()

		self.msg_cnt = self.nodes_dict[0].start_dfu(150000)

		self.res_list = []

		for i in self.nodes_dict.values():
			self.res_list.append(i.print_result())

		self.test_res.write_adv_bearer_full(
			0, self.msg_cnt, self.packet_loss_chance, self.retransmit, self.res_list)

		nx.draw_spring(self.g, with_labels=1)

		plt.savefig("./{}/Graph.pdf".format(self.test_res.dir_path), format="PDF")
		# plt.show()


	def create_network(self):
		for i in self.g.nodes:
			self.nodes_dict[i] = MeshNode(i, 0, self.packet_loss_chance, self.retransmit)
		print(self.nodes_dict)

	def create_edges(self):
		for i in self.g.edges:
			self.nodes_dict[i[0]].add_neighbour_node(self.nodes_dict[i[1]])

x = MeshNetwork(20,10,3)


# a = MeshNode("Anders", 90)
# b = MeshNode("Erik", 69)
# c = MeshNode("Martin", 1)
# d = MeshNode("John", 666)
# e = MeshNode("Sivert", 666)
# f = MeshNode("Mari", 666)
# g = MeshNode("Ellen", 666)

# a.add_neighbour_node(b)
# b.add_neighbour_node(c)
# b.add_neighbour_node(d)


# c.add_neighbour_node(e)
# d.add_neighbour_node(e)

# d.add_neighbour_node(e)
# e.add_neighbour_node(f)
# f.add_neighbour_node(g)

# a.start_dfu(2000000)

# # for i in range(0,10):

# # 	a.advertise_message(i, 75 * i, 75 * i)

# b.print_result()
# c.print_result()
# d.print_result()
# e.print_result()
# f.print_result()
# g.print_result()


# G = nx.Graph()
# G = nx.barabasi_albert_graph(10,2)

# print(G.nodes)
# print(G.edges)

# G.add_node(A)
# G.add_node(2)
# G.add_node(3)
# G.add_node(4)

# G.add_edge(1,A)
# G.add_edge(1,4)
# G.add_edge(3,2)
# G.add_edge(3,1)
# G.add_edge(3,A)

# nx.draw_spring(G, with_labels=1)
# plt.savefig("./test_results/Graph.pdf", format="PDF")
# # print(G.number_of_nodes())

# print(G.nodes)
# print(G.adj[1])

# for i in G.nodes:
# 	try:
# 		i.print_info()
# 	except:
# 		print(0)
# 		pass
# # print(G.nodes(1))

# plt.show()

# qwe = [(0, 2), (0, 3), (0, 7), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 9), (2, 4), (2, 5), (2, 9), (4, 6), (4, 7), (4, 8), (5, 8)]

# print(qwe[0])
# print(qwe[0][0])
# print(qwe[0][1])

# import csv

# G = nx.Graph()
# G = nx.barabasi_albert_graph(10,2)


# G.add_node(1)
# G.add_node(2)
# G.add_node(3)
# G.add_node(4)

# G.add_edge(1,2)
# G.add_edge(1,4)
# G.add_edge(3,2)
# G.add_edge(3,1)
# G.add_edge(3,1)

# print(G.nodes)
# print(G.edges)

# nx.draw_spring(G, with_labels=1)

# plt.show()




# import csv

# G = nx.Graph()

# with open('innovators.csv', 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(G.nodes)
#     writer.writerow(G.edges)



# with open('innovators.csv', 'r') as file:
# 	reader = csv.reader(file)

# 	nodes = next(reader)

# 	for i in nodes:
# 		G.add_node(eval(i))

# 	edges = next(reader)

# 	for item in edges:
# 		G.add_edge(*eval(item))


# print(G.nodes)
# print(G.edges)

# nx.draw_spring(G, with_labels=1)
# plt.show()

def create_network_csv(nodes, edges, file_name):

	G = nx.barabasi_albert_graph(nodes, edges)

	with open('./network_struct_cvs/{}.csv'.format(file_name), 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(G.nodes)
		writer.writerow(G.edges)

def load_network_csv(file_name):
	G = nx.Graph()

	with open('./network_struct_cvs/{}.csv'.format(file_name), 'r') as file:
		reader = csv.reader(file)

		nodes = next(reader)
		for i in nodes:
			G.add_node(eval(i))
		edges = next(reader)
		for item in edges:
			G.add_edge(*eval(item))

	nx.draw_spring(G, with_labels=1)
	plt.show()
# create_network_csv(20, 2, "test_network")
# load_network_csv("test_network")
