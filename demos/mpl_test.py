if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import mplcursors
    import numpy as np

    #  np.random.seed(42)

    #  fig, ax = plt.subplots()
    #  ax.scatter(*np.random.random((2, 26)))
    #  ax.set_title("Mouse over a point")

    #  mplcursors.cursor(hover=True)

    #  plt.show()

    #  fig, axes = plt.subplots(ncols=2)

    #  left_artist = axes[0].plot(range(11))
    #  axes[0].set(title="No box, different position", aspect=1)

    #  right_artist = axes[1].imshow(np.arange(100).reshape(10, 10))
    #  axes[1].set(title="Fancy white background")

    #  # Make the text pop up "underneath" the line and remove the box...
    #  c1 = mplcursors.cursor(left_artist)
    #  @c1.connect("add")
    #  def _(sel):
    #  sel.annotation.set(position=(5, 5))
    #  # Note: Needs to be set separately due to matplotlib/matplotlib#8956.
    #  sel.annotation.set_bbox(None)

    #  # Make the box have a white background with a fancier connecting arrow
    #  c2 = mplcursors.cursor(right_artist)
    #  @c2.connect("add")
    #  def _(sel):
    #  sel.annotation.get_bbox_patch().set(fc="white")
    #  sel.annotation.arrow_patch.set(arrowstyle="simple", fc="white", alpha=.5)

    #  plt.show()

    fig, ax = plt.subplots()
    ax.plot(range(10), "o-")
    ax.set_title(
        'Press "e" to enable/disable the datacursor\n'
        'Press "h" to hide/show any annotation boxes'
    )

    mplcursors.cursor(bindings={"toggle_visible": "h", "toggle_enabled": "e"})

    plt.show()
