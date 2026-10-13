"""Named base-map locations, resolved from the loaded SCX at build time."""
from eudplib import TrgLocation


class Loc:
    city_guard = TrgLocation("city_guard")
    city_capture = TrgLocation("city_capture")
    city_point = TrgLocation("city_point")
    city_spawn = TrgLocation("city_spawn")
    mouse_p1 = TrgLocation("mouse_p1")
    mouse_p2 = TrgLocation("mouse_p2")
    mouse_p3 = TrgLocation("mouse_p3")
    mouse_p4 = TrgLocation("mouse_p4")
    mouse_p5 = TrgLocation("mouse_p5")
    mouse_p6 = TrgLocation("mouse_p6")
    mouse_p7 = TrgLocation("mouse_p7")
    start_p1 = TrgLocation("start_p1")
    start_p2 = TrgLocation("start_p2")
    start_p3 = TrgLocation("start_p3")
    start_p4 = TrgLocation("start_p4")
    start_p5 = TrgLocation("start_p5")
    start_p6 = TrgLocation("start_p6")
    start_p7 = TrgLocation("start_p7")
    command = TrgLocation("command")
    msqc = TrgLocation("msqc")
    anywhere = TrgLocation("Anywhere")


START_LOCATIONS = (Loc.start_p1, Loc.start_p2, Loc.start_p3, Loc.start_p4,
                   Loc.start_p5, Loc.start_p6, Loc.start_p7)
