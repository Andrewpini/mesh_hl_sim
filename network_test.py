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

def create_network_csv(nodes, edges, file_name):

	G = nx.barabasi_albert_graph(nodes, edges)

	plt.clf()
	nx.draw_spring(G, with_labels=1)
	plt.show()

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

	plt.clf()
	nx.draw_spring(G, with_labels=1)
	plt.show()

class MeshNode(object):
	# 4.2.2.7 Publish Retransmit Interval Steps: Minimum 50ms
	# 4.2.19.2 Network Transmit Interval Steps: Minimum random 0-10ms
	# 4.2.20.2 Relay Retransmit Interval Steps: Minimum 10ms

	# Mulig Network Transmit Interval og Relay Retransmit Interval kan nulles ut siden den ene gjelder GATT og den andre ADV Bearer

	def __init__(self, name, number, packet_loss_chance, retransmit):
		self.name = name
		self.number = number
		self.packet_loss_chance = packet_loss_chance

		self.adjecent_nodes = []
		self.msg_cache = []
		self.msg_approved = 0
		self.last_msg_timestamp = 0
		self.retransmit = retransmit

	def reset_node(self):
		self.msg_cache = []
		self.msg_approved = 0
		self.last_msg_timestamp = 0

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

	def __init__(self, node_cnt, packet_loss_chance=0, retransmit=1, network_top=None):
		self.packet_loss_chance = packet_loss_chance
		self.retransmit = retransmit

		if network_top:
			self.g = nx.Graph()
			self.load_network_csv(network_top)
			self.node_cnt = len(self.g.nodes)
		else:
			self.g = nx.barabasi_albert_graph(node_cnt, 2)
			self.node_cnt = node_cnt

		self.nodes_dict = {}
		self.create_network()
		self.create_edges()

	def initiate_dfu(self, origin_node, size):
		test_res = csv_test.TestResults()
		self.msg_cnt = self.nodes_dict[origin_node].start_dfu(size)
		self.res_list = []

		for i in self.nodes_dict.values():
			self.res_list.append(i.print_result())
		self.reset_nodes()

		test_res.write_test_result(
			origin_node, self.msg_cnt, self.packet_loss_chance, self.retransmit, self.res_list)

		plt.savefig("./{}/Graph.pdf".format(test_res.dir_path), format="PDF")

	def create_network(self):
		for i in self.g.nodes:
			self.nodes_dict[i] = MeshNode(i, 0, self.packet_loss_chance, self.retransmit)

	def create_edges(self):
		for i in self.g.edges:
			self.nodes_dict[i[0]].add_neighbour_node(self.nodes_dict[i[1]])
		plt.clf()
		nx.draw_spring(self.g, with_labels=1)

	def reset_nodes(self):
		for i in self.nodes_dict.values():
			i.reset_node()

	def load_network_csv(self, file_name):
		with open('./network_struct_cvs/{}.csv'.format(file_name), 'r') as file:
			reader = csv.reader(file)

			nodes = next(reader)
			for i in nodes:
				self.g.add_node(eval(i))
			edges = next(reader)
			for item in edges:
				self.g.add_edge(*eval(item))

x = MeshNetwork(100, packet_loss_chance=10, retransmit=4, network_top="test_network")
# x = MeshNetwork(30, packet_loss_chance=10, retransmit=3, network_top=None)
x.initiate_dfu(1, 150000)
x.initiate_dfu(0, 150000)

