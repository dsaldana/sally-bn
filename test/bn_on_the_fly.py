from gi.repository import Gtk, GObject
import random

from lib_sallybn.disc_bayes_net.DiscreteBayesianNetworkExt import DiscreteBayesianNetworkExt
from lib_sallybn.disc_bayes_net.BoxDiscreteBN import BoxDiscreteBN

# Create window
window = Gtk.Window()
window.set_size_request(800, 600)

## Discrete bn
disc_bn = DiscreteBayesianNetworkExt()
# Vertex and its states
disc_bn.add_vertex("A", states=["true1", "false1"])
disc_bn.add_vertex("C", states=["true", "false"])
disc_bn.add_vertex("B", states=["true", "false"])

# Edges
disc_bn.add_edge(["A", "B"])
disc_bn.add_edge(["C", "B"])

# CPTs
cprob_b = {
    "['true1', 'true']": [.3, .7],
    "['true1', 'false']": [.9, .1],
    "['false1', 'true']": [.05, .95],
    "['false1', 'false']": [.5, .5]
}
cprob_a = [.3, .7]
cprob_c = [.2, .8]

disc_bn.set_cprob("A", cprob_a)
disc_bn.set_cprob("B", cprob_b)
disc_bn.set_cprob("C", cprob_c)

###### SHOW
box = BoxDiscreteBN(window, disc_bn=disc_bn)
box.on_organize(None)
window.add(box)

print "2a"

new_vertices = []

def opa():
    print "op"
    # time.sleep(2)
    new_vertex = "D " + str(random.random())
    disc_bn.add_vertex(new_vertex)
    new_vertices.append(new_vertex)
    ## edges
    if len(new_vertices) >2:
        de =random.sample(new_vertices,2)
        disc_bn.add_edge(de)
        de =random.sample(new_vertices,2)
        disc_bn.add_edge(de)

    box.on_organize(None)
    print "opa"
    # GObject.idle_add(done, *((task_id,) + args))


for i in range(100):
    update_id = GObject.timeout_add(int(i * 2000), opa)  # t = Thread(target=opa)

# t.start()
# t.daemon = True
GObject.threads_init()  # init threads?

print "1a"

window.show_all()
window.connect("delete-event", Gtk.main_quit)
Gtk.main()
