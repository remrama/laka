# laka
GUI and analysis code for my personal tracking stuff, with strong emphasis on sleep and dream logging.

Data structure follows [BIDS](https://doi.org/10.1038/sdata.2016.44) formatting with custom extensions to accomodate personal tracking data (with an emphasis on optimization for sleep and dreams).

It requires some manual file structure creation before anything will work.


### Sleep logging GUI
The focus of this is to track dream content, so I made a python GUI with PyQt that helps to systematize the logging of dream content.

Initializing the GUI with `run.py` **creates a new session** and opens a session window (`winSession.py`, a `QMainWindow` object). This window is very minimal, and should be opened _before_ going to sleep, as it timestamps the start of the session as a new row in the subject's `*_sessions.tsv` file.

From the session window, there is a button to initialize a new arousal window (`winArousal.py`, also a `QMainWindow` object). This will **create a new arousal** (also appending the subject/session's `*_arousals.tsv` file), and allows for entries of information about dream content.


### Data collected
* **sleep**
    - tracked with [Sleep as Android](https://sleep.urbandroid.org) every night (complemented with heart rate via Mi Band Tools app and Xiaomi Mi Band)
    - recorded with [Hypnodyne Zmax](http://hypnodynecorp.com/) occasionally (~2x per week)
* **activities**
    - recorded as much as possible with [Nomie](https://nomie.app/)