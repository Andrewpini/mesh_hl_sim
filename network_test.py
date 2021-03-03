import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import time
import csv
import time

import csv_test

# Constants
ADV_INTERVAL_MS = 25
GATT_INTERVAL_MS = 20
MSG_PAYLOAD_SIZE = 11
PACKET_ON_AIR_TIME_US = 376
GATT_CHN_CNT = 37
MS_PER_SEC = 1000
US_PER_SEC = 1000000

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

class GattMsg(object):
	def __init__(self, origin, tid, receiver_list):
		self.origin = origin
		self.tid = tid
		self.receiver_list = receiver_list
		try:
			self.receiver_list.remove(origin)
		except:
		    pass


	def msg_fetch(self, node_id):
		if node_id in self.receiver_list:
			# self.receiver_list.remove(node_id)
			return True
		return False

	def check_for_clear(self, node_id):
		try:
			# print("Remaining list: {}".format(self.receiver_list))
			# print("node Id: {}".format(node_id))
			self.receiver_list.remove(node_id)
		except:
		    pass

		if not self.receiver_list:
			return True
		return False

	def check_for_empty(self):
		if not self.receiver_list:
			return True
		return False

	# def receiver_list_set(self, receivers):
	#         self.receiver_list = receivers


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
		self.uniform_noice = uniform_noice / 100
		self.total_loss_chance = uniform_noice / 100

		self.adjacent_nodes = []
		self.connected_nodes = []
		self.msg_cache_list = []
		self.msg_received = 0
		self.last_msg_timestamp = 0
		self.retransmit = retransmit

		self.adv_queue = []
		self.incoming_msg_queue = []
		self.is_dfu_origin = False
		self.pending_update = False
		self.peak_buf_size = 0

		self.adv_msg_sent_list = [0 for i in range(int(MS_PER_SEC/ADV_INTERVAL_MS))]
		self.gatt_msg_sent_list = [
			0 for i in range(int(MS_PER_SEC/GATT_INTERVAL_MS))]
		self.mean_loss_chance = self.uniform_noice

		self.max_buf_size = None
		self.disable_internal_noise = False

	def reset_node(self):
		self.msg_cache_list = []
		self.msg_received = 0
		self.last_msg_timestamp = 0
		self.peak_buf_size = 0
		self.is_dfu_origin = False
		self.pending_update = False

		self.adv_msg_sent_list = [0 for i in range(int(MS_PER_SEC/ADV_INTERVAL_MS))]
		self.gatt_msg_sent_list = [
			0 for i in range(int(MS_PER_SEC/GATT_INTERVAL_MS))]
		self.mean_loss_chance = self.uniform_noice

	def adv_dfu_start(self, n_bytes):
		self.is_dfu_origin = True
		dfu_msg_cnt = math.ceil(n_bytes / MSG_PAYLOAD_SIZE)
		for i in range(1, dfu_msg_cnt + 1):
			for _ in range(self.retransmit):
				self.adv_queue.append(i)
			self.msg_received += 1
		return dfu_msg_cnt

	def adv_msg_send(self, time):
		if time % ADV_INTERVAL_MS is not 0:
			return True
		try:
			tid = self.adv_queue.pop(0)
		except:
			# No message to advertise
			self.adv_sent_update(0)
			return False

		if self.is_dfu_origin:
			self.cache_entry_add(tid)
			self.last_msg_timestamp = time

		self.adv_sent_update(1)
		for node in self.connected_nodes:
			node.adv_msg_receive(tid, time, self.name)
		return True

	def adv_msg_receive(self, tid, timestamp, src):
		if self.adv_was_msg_received(src):

			if tid in self.msg_cache_list:
				return

			if self.max_buf_size and (math.ceil(len(self.adv_queue) / self.retransmit)) >= self.max_buf_size:
			    return

			self.pending_update = True
			self.cache_entry_add(tid)
			self.msg_received += 1
			self.last_msg_timestamp = timestamp

			for _ in range(self.retransmit):
				self.incoming_msg_queue.append(tid)
			return

	def gatt_dfu_start(self, n_bytes):
		self.is_dfu_origin = True
		dfu_msg_cnt = math.ceil(n_bytes / MSG_PAYLOAD_SIZE)
		for i in range(1, dfu_msg_cnt + 1):
			for node in self.connected_nodes:
				self.adv_queue.append([node.name, i])
			self.msg_received += 1
		return dfu_msg_cnt

	def gatt_msg_send(self, time):
		if time % GATT_INTERVAL_MS is not 0:
			return True
		try:
			entry = self.adv_queue.pop(0)
			self.gatt_sent_update(0)
		except:
			return False
		if self.is_dfu_origin:
			self.cache_entry_add(entry[1])
			self.last_msg_timestamp = time

		self.gatt_sent_update(1)
		for node in self.connected_nodes:
			if node.name is entry[0]:
				res = node.gatt_msg_receive(entry[1], time, self.name)
				if not res:
					self.adv_queue.insert(0, entry)
		return True

	def gatt_msg_receive(self, tid, timestamp, src):
		if self.gatt_was_msg_received(src):
			if self.is_dfu_origin:
				return True
			if tid in self.msg_cache_list:
				return True

			if self.max_buf_size and (math.ceil(
				len(self.adv_queue) / max( (len(self.connected_nodes) - 1), 1)) >= self.max_buf_size):
			    return False

			self.pending_update = True

			self.cache_entry_add(tid)
			self.msg_received += 1
			self.last_msg_timestamp = timestamp

			for node in self.connected_nodes:
				if node.name is src:
					continue
				self.incoming_msg_queue.append([node.name, tid])
			return True
		return False

	def gatt_dfu_start2(self, n_bytes):
		self.is_dfu_origin = True
		dfu_msg_cnt = math.ceil(n_bytes / MSG_PAYLOAD_SIZE)
		for i in range(1, dfu_msg_cnt + 1):
			self.adv_queue.append(GattMsg(self.name, i, [c.name for c in self.connected_nodes]))
			# print(self.adv_queue)
			# print(self.connected_nodes[0].name)
			# for node in self.connected_nodes:
			# 	self.adv_queue.append([node.name, i])
			self.msg_received += 1
		return dfu_msg_cnt

	def gatt_msg_send2(self, time):
		if time % GATT_INTERVAL_MS is not 0:
			return True

		if not self.adv_queue:
			# print(self.connected_nodes)
			self.gatt_sent_update(0)
			return False

		self.gatt_sent_update(1)
		for node in self.connected_nodes:
			# print("Sending to node {} adv queue: {}".format(node.name, len(self.adv_queue)))
			for i, j in enumerate(self.adv_queue):
				# print(j.receiver_list)
				ret = j.msg_fetch(node.name)
				if ret:
					# print("asdasd")
					res = node.gatt_msg_receive2(j.tid, time, self.name)
					if res:

						if self.is_dfu_origin:
							self.cache_entry_add(j.tid)
							self.last_msg_timestamp = time
						if j.check_for_clear(node.name):
							self.adv_queue.pop(i)
							# print(self.adv_queue)
					break
		return True

	def gatt_msg_receive2(self, tid, timestamp, src):
		if self.gatt_was_msg_received(src):
			# print("received")
			if self.is_dfu_origin:
				return True
			if tid in self.msg_cache_list:
				return True
			# if self.max_buf_size and (math.ceil(
			# 	len(self.adv_queue) / max( (len(self.connected_nodes) - 1), 1)) >= self.max_buf_size):
			#     return False
			if self.max_buf_size and (len(self.adv_queue) >= self.max_buf_size):
			    return False

			self.pending_update = True

			self.cache_entry_add(tid)
			self.msg_received += 1
			self.last_msg_timestamp = timestamp

			reciever_list = []
			for node in self.connected_nodes:
				if node.name is src:
					continue
				reciever_list.append(node.name)
			if reciever_list:
				self.incoming_msg_queue.append(GattMsg(src, tid, reciever_list))
			return True
		return False

	def adv_sent_update(self, adv):
		self.adv_msg_sent_list.pop(0)
		self.adv_msg_sent_list.append(adv)

	def gatt_sent_update(self, gatt):
		self.gatt_msg_sent_list.pop(0)
		self.gatt_msg_sent_list.append(gatt)

	def adv_self_noise_calc(self):
		if self.disable_internal_noise:
		    return 1

		return 1 - sum(self.adv_msg_sent_list) * PACKET_ON_AIR_TIME_US / US_PER_SEC

	def gatt_self_noise_calc(self):
		if self.disable_internal_noise:
		    return 1
		return 1 - sum(self.gatt_msg_sent_list) * PACKET_ON_AIR_TIME_US / US_PER_SEC / GATT_CHN_CNT

	def adv_queue_update(self):
		if self.pending_update:
			self.adv_queue.extend(self.incoming_msg_queue)
			self.incoming_msg_queue = []
			self.pending_update = False
			self.peak_buf_size = max(self.peak_buf_size, math.ceil(
				len(self.adv_queue) / self.retransmit))

	def gatt_queue_update(self):
		if self.pending_update:
			self.adv_queue.extend(self.incoming_msg_queue)
			self.incoming_msg_queue = []
			self.pending_update = False
			self.peak_buf_size = max(self.peak_buf_size, len(self.adv_queue))


	def add_connected_node(self, node):
		if node not in self.connected_nodes:
			self.connected_nodes.append(node)
			node.connected_nodes.append(self)
			# print("Connected {}".format(node.connected_nodes))

	def add_adjacent_node(self, node):
		if node not in self.adjacent_nodes:
			self.adjacent_nodes.append(node)
			node.adjacent_nodes.append(self)

	def cache_entry_add(self, entry):
		if len(self.msg_cache_list) >= 200:
			self.msg_cache_list.pop(0)
		self.msg_cache_list.append(entry)

	def adv_was_msg_received(self, src):
		temp = 1
		for node in self.adjacent_nodes:
			if node.name is src:
				continue
			temp = temp * node.adv_self_noise_calc()
		internal_noise = 1 - temp

		self.total_loss_chance = self.uniform_noice + internal_noise
		self.mean_loss_chance = (self.mean_loss_chance + self.total_loss_chance) / 2
		return random.random() > self.total_loss_chance

	def gatt_was_msg_received(self, src):
		temp = 1
		for node in self.adjacent_nodes:
			if node.name is src:
				continue
			temp = temp * node.gatt_self_noise_calc()
		internal_noise = 1 - temp
		self.total_loss_chance = self.uniform_noice + internal_noise
		self.mean_loss_chance = (self.mean_loss_chance + self.total_loss_chance) / 2
		return random.random() > self.total_loss_chance

class MeshNetwork(object):

	def __init__(self, uniform_noice, retransmit, network_conn_top, network_adj_top=None):
		self.uniform_noice = uniform_noice
		self.retransmit = retransmit
		self.nodes_dict = {}

		self.connection_network = nx.Graph()
		self.adjacent_network = nx.Graph()
		self.load_network_csv(network_conn_top, network_adj_top)
		self.create_network()
		self.create_edges()

	def adv_dfu_initiate(self, test_name, origin_node, size, test_cnt):
		self._dfu_initiate(origin_node, size, test_cnt, "{}_ADVx{}".format(
			test_name, self.retransmit), is_adv_bearer=True)

	def gatt_dfu_initiate(self, test_name, origin_node, size, test_cnt):
		self._dfu_initiate(origin_node, size, test_cnt,
				   "{}_GATT".format(test_name), is_adv_bearer=False)

	def _gatt_dfu_run(self, origin_node, size):
		self.msg_cnt = self.nodes_dict[origin_node].gatt_dfu_start2(size)
		test = True
		run_time = GATT_INTERVAL_MS
		while test:
			test = False
			for i in self.nodes_dict.values():
				test |= i.gatt_msg_send2(run_time)
				# print(test)
			for i in self.nodes_dict.values():
				i.gatt_queue_update()
			run_time += GATT_INTERVAL_MS
			# time.sleep(1)
			# print("Tic")

	def _adv_dfu_run(self, origin_node, size):
		self.msg_cnt = self.nodes_dict[origin_node].adv_dfu_start(size)
		test = True
		time = ADV_INTERVAL_MS
		while test:
			test = False
			for i in self.nodes_dict.values():
				test |= i.adv_msg_send(time)
			for i in self.nodes_dict.values():
				i.adv_queue_update()
			time += ADV_INTERVAL_MS

	def _dfu_initiate(self, origin_node, size, test_cnt, test_name, is_adv_bearer):
		test_res = csv_test.TestResults(test_name)
		res_dict = {}

		for i in self.nodes_dict.values():
			res_dict[i.name] = {"last_ts": 0, "msg_received": 0, "mean_noise": 0,
			    "peak_buf_size": 0, "link_cnt": len(i.connected_nodes), "adj_cnt": len(i.adjacent_nodes)}

		for j in range(test_cnt):
			if is_adv_bearer:
				self._adv_dfu_run(origin_node, size)
			else:
				self._gatt_dfu_run(origin_node, size)

			for i in self.nodes_dict.values():
				res_dict[i.name]["last_ts"] += i.last_msg_timestamp
				res_dict[i.name]["msg_received"] += i.msg_received
				res_dict[i.name]["mean_noise"] += i.mean_loss_chance * 100
				res_dict[i.name]["peak_buf_size"] = max(
					i.peak_buf_size, res_dict[i.name]["peak_buf_size"])
			print("{} simulation done".format(j))
			self.reset_nodes()

		for i in res_dict.values():
			i["last_ts"] = i["last_ts"] / test_cnt
			i["msg_received"] = i["msg_received"] / test_cnt
			i["mean_noise"] = i["mean_noise"] / test_cnt

		test_res.write_test_result(
			origin_node, self.msg_cnt, self.uniform_noice, self.retransmit, res_dict)
		plt.savefig("./{}/Graph.pdf".format(test_res.dir_path), format="PDF")
		print("\nDFU simulation complete\n")

	def create_network(self):
		for i in self.connection_network.nodes:
			self.nodes_dict[i] = MeshNode(
				i, self.uniform_noice, self.retransmit)

	def create_edges(self):
		for i in self.connection_network.edges:
			self.nodes_dict[i[0]].add_connected_node(self.nodes_dict[i[1]])
		for j in self.adjacent_network.edges:
			self.nodes_dict[j[0]].add_adjacent_node(self.nodes_dict[j[1]])

		plt.clf()
		nx.draw_spring(self.connection_network, with_labels=1)

	def reset_nodes(self):
		for i in self.nodes_dict.values():
			i.reset_node()

	def buf_max_set(self, val):
		for i in self.nodes_dict.values():
			i.max_buf_size = val

	def internal_noise_disable(self, is_true):
		for i in self.nodes_dict.values():
			i.disable_internal_noise = is_true

	def load_network_csv(self, conn_file_name, adj_file_name):
		with open('./network_struct_cvs/{}.csv'.format(conn_file_name), 'r') as conn_file:
			reader = csv.reader(conn_file)

			conn_nodes = next(reader)
			for i in conn_nodes:
				self.connection_network.add_node(eval(i))
			conn_edges = next(reader)
			for j in conn_edges:
				self.connection_network.add_edge(*eval(j))

		if not adj_file_name:
			for i in conn_nodes:
				self.adjacent_network.add_node(eval(i))
			for j in conn_edges:
				self.adjacent_network.add_edge(*eval(j))
		else:
			with open('./network_struct_cvs/{}.csv'.format(adj_file_name), 'r') as adj_file:
				reader = csv.reader(adj_file)

				adj_nodes = next(reader)
				for i in adj_nodes:
					self.adjacent_network.add_node(eval(i))
				adj_edges = next(reader)
				for j in adj_edges:
					self.adjacent_network.add_edge(*eval(j))

	def load_noice_csv(self, file_name):
		with open('./network_struct_cvs/{}.csv'.format(file_name), 'r') as file:
			reader = csv.reader(file)

			noice = next(reader)
			i = 0
			for item in noice:
				self.nodes_dict[i].total_loss_chance = eval(item)
				i += 1


# a = MeshNode(0, 0, 1)
# b.add_connected_node(a)
# x.load_noice_csv("nice_test")

## Used to generate final data:
# for i in range(1, 5 + 1):
# 	x = MeshNetwork(uniform_noice=10,
# 			retransmit=i, network_conn_top="net_3linkmax")
# 	x.buf_max_set(64)
# 	x.adv_dfu_initiate("net_3linkmax", 0, 150000, 100)

# # Used to generate final data:
# x = MeshNetwork(uniform_noice=10,
# 		retransmit=1, network_conn_top="net_3linkmax")
# x.buf_max_set(8)
# x.gatt_dfu_initiate("RE_net_3linkmax_buf8", 0, 150000, 100)

# Used to generate final data:
# x = MeshNetwork(uniform_noice=10,
                # retransmit=4, network_conn_top="net_3linkmax_broken")
# x.buf_max_set(8)
# x.adv_dfu_initiate("net_3linkmax_broken", 0, 150000, 100)
# x.gatt_dfu_initiate("RE_net_3linkmax_broken_buf8", 0, 150000, 100)

## Used to generate final data:
# x = MeshNetwork(uniform_noice=10,
#                 retransmit=3, network_conn_top="net_broken_tree", network_adj_top="net_3linkmax_broken")
# x.buf_max_set(8)
# x.gatt_dfu_initiate("RE_net_broken_tree_buf256", 0, 150000, 100)

# ## Used to generate final data:
x = MeshNetwork(uniform_noice=10,
                retransmit=3, network_conn_top="net_broken_snake", network_adj_top="net_3linkmax_broken")
x.buf_max_set(8)
x.gatt_dfu_initiate("net_broken_snake", 0, 150000, 100)

# ## Used to generate final data:
# for i in range(1, 7 + 1):
# 	x = MeshNetwork(uniform_noice=10,
# 			retransmit=i, network_conn_top="net_adv_chain_sample")
# 	x.buf_max_set(16)
# 	x.internal_noise_disable(True)
# 	x.adv_dfu_initiate("net_adv_chain_sample", 0, 150000, 100)

# ## Used to generate final data:
# x = MeshNetwork(uniform_noice=10,
#                 retransmit=4, network_conn_top="net_3linkmax_broken")
# x.buf_max_set(64)
# x.internal_noise_disable(False)
# x.adv_dfu_initiate("net_3linkmax_broken", 12, 150000, 1000)

# ## Used to generate final data:
# for i in range(1, 7 + 1):
# 	x = MeshNetwork(uniform_noice=10,
# 			retransmit=i, network_conn_top="net_adv_triangle_sample")
# 	x.buf_max_set(16)
# 	x.internal_noise_disable(True)
# 	x.nodes_dict[1].uniform_noice = 0
# 	x.nodes_dict[1].total_loss_chance = 0
# 	x.adv_dfu_initiate("net_adv_triangle_sample", 0, 150000, 100)

# ## Used to generate final data:
# x = MeshNetwork(uniform_noice=10,
#                 retransmit=3, network_conn_top="net_broken_tree", network_adj_top="net_3linkmax_broken")
# x.internal_noise_disable(True)
# x.buf_max_set(256)
# x.gatt_dfu_initiate("net_broken_tree_no_buf_lim", 0, 150000, 100)


# ## Used to generate final data:
# x = MeshNetwork(uniform_noice=10,
#                 retransmit=3, network_conn_top="net_broken_snake", network_adj_top="net_3linkmax_broken")
# x.internal_noise_disable(True)
# # x.nodes_dict[0].uniform_noice = 50
# x.nodes_dict[1].total_loss_chance = 90

# x.buf_max_set(256)
# x.gatt_dfu_initiate("net_broken_snake", 0, 150000, 1)


# x = MeshNetwork(uniform_noice=10,
#                 retransmit=1, network_conn_top="net_3linkmax_broken")
# x.buf_max_set(256)
# x.internal_noise_disable(False)
# # x.nodes_dict[14].retransmit = 4

# x.adv_dfu_initiate("net_3linkmax_broken", 0, 150000, 1)










# x = MeshNetwork(uniform_noice=10,
#                 retransmit=3, network_conn_top="net_3linkmax_broken", network_adj_top="net_3linkmax_broken")
# # x.internal_noise_disable(True)
# x.buf_max_set(8)
# x.gatt_dfu_initiate("test_del", 0, 150000, 1)







# Anders = MeshNode(0,0,1)
# John = MeshNode(1,0,1)
# Sivert = MeshNode(2,0,1)

# a = GattMsg(Anders,1, [John,Anders])
# b = GattMsg(Anders,2, [John,Sivert,Anders])

# Anders.add_connected_node(John)
# Anders.add_connected_node(Sivert)
# print(John.connected_nodes, 123557)

# # Anders.adv_queue.append(a)
# Anders.adv_queue.append(b)

# print(Anders.adv_queue)
# Anders.gatt_msg_send2(20)
# print(John.incoming_msg_queue)
# print(Sivert.incoming_msg_queue)
# print(Anders.adv_queue)

# print(Sivert.adv_queue)

# Sivert.gatt_queue_update()
# print(Sivert.adv_queue)

# Sivert.gatt_msg_send2(40)
