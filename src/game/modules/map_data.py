"""Named base-map locations, resolved from the loaded SCX at build time."""
from eudplib import EncodeLocation


class Loc:
    city_guard = EncodeLocation("city_guard")
    city_capture = EncodeLocation("city_capture")
    city_point = EncodeLocation("city_point")
    city_spawn = EncodeLocation("city_spawn")
    mouse_p1 = EncodeLocation("mouse_p1")
    mouse_p2 = EncodeLocation("mouse_p2")
    mouse_p3 = EncodeLocation("mouse_p3")
    mouse_p4 = EncodeLocation("mouse_p4")
    mouse_p5 = EncodeLocation("mouse_p5")
    mouse_p6 = EncodeLocation("mouse_p6")
    mouse_p7 = EncodeLocation("mouse_p7")
    start_p1 = EncodeLocation("start_p1")
    start_p2 = EncodeLocation("start_p2")
    start_p3 = EncodeLocation("start_p3")
    start_p4 = EncodeLocation("start_p4")
    start_p5 = EncodeLocation("start_p5")
    start_p6 = EncodeLocation("start_p6")
    start_p7 = EncodeLocation("start_p7")
    command = EncodeLocation("command")
    msqc = EncodeLocation("msqc")
    anywhere = EncodeLocation("Anywhere")


START_LOCATIONS = (Loc.start_p1, Loc.start_p2, Loc.start_p3, Loc.start_p4,
                   Loc.start_p5, Loc.start_p6, Loc.start_p7)
