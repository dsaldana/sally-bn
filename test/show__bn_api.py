from gi.repository import Gtk
from lib_sallybn.disc_bayes_net.BoxDiscreteBN import BoxDiscreteBN
import os

# working directory
os.chdir("../")

# Load file
file = "examples/simplebn.sly"
# file = "examples/disc_bn_recommendation_letter.txt"
# Create window
window = Gtk.Window()
window.set_size_request(800, 600)

## Box BM
box = BoxDiscreteBN(window)
box.load_bn_from_file(file)
window.add(box)

window.show_all()
Gtk.main()