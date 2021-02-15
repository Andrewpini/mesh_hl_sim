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

# (47 bytes * 8 bit/byte * 1us/bit) / 25ms (interval+delay)
IS_SENDING_PROB = 0.01504

def create_network_csv(nodes, edges, file_name):

	G = nx.barabasi_albert_graph(nodes, edges)

	edge_n_dict = {}
	for i in G.nodes:
		n_edges = 0
		for j in G.edges:
			if (j[0] == i) or (j[1] is i):
				n_edges +=1
		edge_n_dict[str(i)] = n_edges

	for x, y in edge_n_dict.items():
		print("Node: {}, {} edges".format(x, y))

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

	# Selvstøy bør simuleres. Slik det er per nå så får man ingen penalty for selvstøy, noe som innebærer at man alltid får bedre performance ved økt antall links/repeats.

	# Tanke: I GATT solution trenger man ikke nødvendigvis å bruke alle tilgjengelige linker. Kan lage en "GATT-snake". Latency i DFU-sammenheng er ikke så interesant, bare throughput

	# Antallet linker i simulert nettverk trenger/bør ikke være mer en 3 per node.

	# Simulering av GATT connections kan gjøres på følgende måte: Kjør simulering med 7.5-20 ms intervall Conn interval (helst 20?). Dette vil representere tiden det tar å forsøke å overføre en pakke over en GATT connection. På hver link så legger man til et interval per forsøk på å overføre pakken. Så snart overføringen er fullført så går man til neste connection inntil man har gått gjennom alle. For å forenkle prosessen ser vi bort fra tiden det tar med ctx switch mellom de ulike connectionene.

	def __init__(self, name, uniform_noice, retransmit):
		self.name = name
		self.uniform_noice = uniform_noice
		self.total_loss_chance = uniform_noice
		self.self_noice = 0

		self.adjecent_nodes = []
		self.msg_cache = []
		self.msg_approved = 0
		self.last_msg_timestamp = 0
		self.retransmit = retransmit

	def reset_node(self):
		self.msg_cache = []
		self.msg_approved = 0
		self.last_msg_timestamp = 0

	def set_self_noice(self):
		cnt = len(self.adjecent_nodes)
		if cnt > 0:
			self.total_loss_chance = (
				1 - (pow(1 - IS_SENDING_PROB, cnt))) * 100 + self.uniform_noice


	def start_dfu(self, n_bytes):
		dfu_msg_cnt = math.ceil(n_bytes / MSG_PAYLOAD_SIZE)
		timestamp = 0
		# start = time.time()
		for i in range(1, dfu_msg_cnt + 1):
			if i % 100 is 0:
				print(i)
			self.add_cache_entry(i)
			self.msg_approved += 1
			if timestamp > self.last_msg_timestamp:
				self.last_msg_timestamp = timestamp
			timestamp = self.advertise_message(i, timestamp)
			# timestamp += 75
		# print("Messages sent: {}, Time expired: {}".format(dfu_msg_cnt, timestamp))
		# stop = time.time()
		# print("Run took: {}".format(stop - start))
		return dfu_msg_cnt

	def start_dfu_gatt(self, n_bytes):
		dfu_msg_cnt = math.ceil(n_bytes / MSG_PAYLOAD_SIZE)
		timestamp = 0
		# start = time.time()
		for i in range(1, dfu_msg_cnt + 1):
			if i % 100 is 0:
				print(i)
			self.add_cache_entry(i)
			self.msg_approved += 1
			if timestamp > self.last_msg_timestamp:
				self.last_msg_timestamp = timestamp
			timestamp = self.gatt_message_send(i, timestamp)
		# print("Messages sent: {}, Time expired: {}".format(dfu_msg_cnt, timestamp))
		# stop = time.time()
		# print("Run took: {}".format(stop - start))
		return dfu_msg_cnt

	def advertise_message(self, tid, timestamp):
		print("Node {} Advertising. Tid: {}, Time: {}".format(self.name, tid, timestamp))
		temp_timestamp = timestamp
		for _ in range(self.retransmit):
			temp_timestamp += ADV_TIME
			for node in self.adjecent_nodes:
				node.start_receive_adv_msg(tid, temp_timestamp)
		return temp_timestamp

	def gatt_message_send(self, tid, timestamp):
		temp_timestamp = timestamp

		for node in self.adjecent_nodes:
			i = 0
			success = False

			while not success:
				i += 1
				temp_timestamp += 20
				success |= node.start_receive_gatt_msg(tid, temp_timestamp)
		return temp_timestamp

	def add_neighbour_node(self, node):
		if node not in self.adjecent_nodes:
			self.adjecent_nodes.append(node)
			node.adjecent_nodes.append(self)

	def add_cache_entry(self, entry):
		if len(self.msg_cache) >= 10:
			self.msg_cache.pop(0)

		self.msg_cache.append(entry)

	def start_receive_adv_msg(self, tid, timestamp):
		if self.was_msg_recieved(self.total_loss_chance):

			if tid in self.msg_cache:
				return True
			self.add_cache_entry(tid)
			self.msg_approved += 1
			if timestamp > self.last_msg_timestamp:
				self.last_msg_timestamp = timestamp

			self.advertise_message(tid, timestamp)
			return True

		return False

	def start_receive_gatt_msg(self, tid, timestamp):
		if self.was_msg_recieved(self.total_loss_chance):

			if tid in self.msg_cache:
				return True
			self.add_cache_entry(tid)
			self.msg_approved += 1
			if timestamp > self.last_msg_timestamp:
				self.last_msg_timestamp = timestamp

			self.gatt_message_send(tid, timestamp)
			return True

		return False

	@staticmethod
	def was_msg_recieved(loss_chance):
		return random.random() > loss_chance / 100

	def print_result(self):
		return [self.name, len(self.adjecent_nodes), self.total_loss_chance, self.last_msg_timestamp, self.msg_approved]

	def print_result2(self):
		return [self.last_msg_timestamp, self.msg_approved]

	def print_gen_info(self):
		return [self.name, len(self.adjecent_nodes), self.total_loss_chance, ]


class MeshNetwork(object):

	def __init__(self, node_cnt, uniform_noice=0, retransmit=1, network_top=None):
		self.uniform_noice = uniform_noice
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
		self.calc_self_noice()

	def initiate_dfu(self, origin_node, size, test_cnt):
		test_res = csv_test.TestResults()

		self.res_list = []
		res_dict = {}
		for i in self.nodes_dict.values():
			res_dict[i.name] = [0,0]

		for _ in range(test_cnt):
			self.msg_cnt = self.nodes_dict[origin_node].start_dfu(size)
			for i in self.nodes_dict.values():
				val = i.print_result2()
				res_dict[i.name][0] += val[0]
				res_dict[i.name][1] += val[1]
			self.reset_nodes()

		for i in self.nodes_dict.values():
			self.res_list.append(i.print_gen_info() + [i / test_cnt for i in res_dict[i.name]])
		test_res.write_test_result(
			origin_node, self.msg_cnt, self.uniform_noice, self.retransmit, self.res_list)

		plt.savefig("./{}/Graph.pdf".format(test_res.dir_path), format="PDF")

	def initiate_dfu_gatt(self, origin_node, size, test_cnt):
		test_res = csv_test.TestResults()

		self.res_list = []
		res_dict = {}
		for i in self.nodes_dict.values():
			res_dict[i.name] = [0,0]

		for _ in range(test_cnt):
			self.msg_cnt = self.nodes_dict[origin_node].start_dfu_gatt(size)
			for i in self.nodes_dict.values():
				val = i.print_result2()
				res_dict[i.name][0] += val[0]
				res_dict[i.name][1] += val[1]
			self.reset_nodes()

		for i in self.nodes_dict.values():
			self.res_list.append(i.print_gen_info() + [i / test_cnt for i in res_dict[i.name]])
		test_res.write_test_result(
			origin_node, self.msg_cnt, self.uniform_noice, self.retransmit, self.res_list)

		plt.savefig("./{}/Graph.pdf".format(test_res.dir_path), format="PDF")

	def create_network(self):
		for i in self.g.nodes:
			self.nodes_dict[i] = MeshNode(
				i, self.uniform_noice, self.retransmit)

	def create_edges(self):
		for i in self.g.edges:
			self.nodes_dict[i[0]].add_neighbour_node(self.nodes_dict[i[1]])
		plt.clf()
		nx.draw_spring(self.g, with_labels=1)

	def calc_self_noice(self):
		for i in self.g.nodes:
			self.nodes_dict[i].set_self_noice()

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

	def load_noice_csv(self, file_name):
		with open('./network_struct_cvs/{}.csv'.format(file_name), 'r') as file:
			reader = csv.reader(file)

			noice = next(reader)
			i = 0
			for item in noice:
				self.nodes_dict[i].total_loss_chance = eval(item)
				i += 1


# x = MeshNetwork(100, uniform_noice=10,
#                 retransmit=4, network_top="test_network")
# x = MeshNetwork(30, uniform_noice=10, retransmit=3, network_top=None)
# x.initiate_dfu(1, 150000)
# x.initiate_dfu(0, 150000)


# x = MeshNetwork(1, uniform_noice=10,
#                 retransmit=3, network_top="custom_mesh")
# x.initiate_dfu(5, 15000000)

# x = MeshNetwork(1, uniform_noice=10,
#                 retransmit=3, network_top="custom_mesh_tail")
# x.initiate_dfu(5, 150000)

# x = MeshNetwork(1, uniform_noice=10,
#                 retransmit=3, network_top="custom_mesh_tail")
# x.initiate_dfu(21, 150000)

# x = MeshNetwork(1, uniform_noice=10,
#                 retransmit=3, network_top="net_3linkmax")
# x.initiate_dfu(0, 11)

# create_network_csv(8, 2, "net2")


# a = MeshNode(0, 50, 1)
# b = MeshNode(1, 50, 1)
# c = MeshNode(2, 50, 1)
# d = MeshNode(3, 50, 1)
# e = MeshNode(4, 50, 1)
# f = MeshNode(5, 50, 1)

# b.add_neighbour_node(a)
# c.add_neighbour_node(a)
# d.add_neighbour_node(a)
# e.add_neighbour_node(a)
# f.add_neighbour_node(a)

# a.set_self_noice()
# asd = a.self_noice + a.uniform_noice
# print(asd)
# a.gatt_message_send(0,0,0)


x = MeshNetwork(1, uniform_noice=10,
                retransmit=3, network_top="net_3linkmax")

# x.load_noice_csv("nice_test")

# x.initiate_dfu_gatt(0, 150000, 10)
x.initiate_dfu(0, 33, 1)

# def test(i):
# 	return min(100, 0.7 + pow(.9*(i - 1), 2.4))
# prev = 0
# for i in range(1,30):
# #     print("Adj nodes: {}, loss chance: {:.2f}%".format(i, test(i)))
# #     print("Adj nodes: {}, loss chance: {}".format(i, pow(1.7,i)))
# 	curr = (1 - (pow(.985,i))) * 100
# 	# print("Diff: {}".format(prev - curr))
# 	print("Adj nodes: {}, loss chance: {}".format(i, curr))
# 	prev = curr
