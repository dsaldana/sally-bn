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
import Tkinter as tk

from lib_sallybn.util import resources


def show_splash(time=2):
    # create a splash screen, 80% of display screen size, centered,
    # displaying a GIF image with needed info, disappearing after 5 seconds
    splash_width = 500
    splash_height = 234

    root = tk.Tk()
    # show no frame
    root.overrideredirect(True)
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(
        '%dx%d+%d+%d' % (splash_width, splash_height, width / 2.0 - splash_width, height / 2.0 - splash_height))
    # root.geometry('%dx%d+%d+%d' % (800, 600, 1160, 380))
    image_file = resources.SPLASH_IMG
    # # use Tkinter's PhotoImage for .gif files
    image = tk.PhotoImage(file=image_file)
    canvas = tk.Canvas(root, height=splash_height, width=splash_width, bg="blue")
    canvas.create_image(splash_width / 2.0, splash_height / 2.0, image=image)
    canvas.pack()
    # show the splash screen for 5000 milliseconds then destroy
    root.after(time * 1000, root.destroy)
    root.mainloop()
