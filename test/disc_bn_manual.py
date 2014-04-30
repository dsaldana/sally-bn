from gi.repository import Gtk

from lib_sallybn.disc_bayes_net.DiscreteBayesianNetworkExt import DiscreteBayesianNetworkExt
from lib_sallybn.disc_bayes_net.BoxDiscreteBN import BoxDiscreteBN

## create bn

## load rules

##



# Create window
window = Gtk.Window()
window.set_size_request(800, 600)

## Discrete bn
disc_bn = DiscreteBayesianNetworkExt()
# Vertex
disc_bn.add_vertex("A")
disc_bn.add_vertex("B")
disc_bn.add_vertex("C")
# Edges
disc_bn.add_edge(["A", "B"])
disc_bn.add_edge(["C", "B"])
# States
# disc_bn.add_state("A", "true")
# disc_bn.add_state("A", "false")
# disc_bn.add_state("C", "true")
# disc_bn.add_state("C", "false")
# disc_bn.add_state("B", "true")
# disc_bn.add_state("B", "false")

# CPTs
cprob_b = {
    "['true', 'true']": [.3, .7],
    "['true', 'false']": [.9, .1],
    "['false', 'true']": [.05, .95],
    "['false', 'false']": [.5, .5]
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
window.show_all()
window.connect("delete-event", Gtk.main_quit)
Gtk.main()