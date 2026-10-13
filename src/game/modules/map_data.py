"""Named base-map locations, resolved from the loaded SCX at build time."""
from eudplib import EncodeLocation

map_version = "NoE3s0.01"


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
    strasbourg = EncodeLocation("strasbourg")
    ulm = EncodeLocation("ulm")
    augsburg = EncodeLocation("augsburg")
    munich = EncodeLocation("munich")
    nuremberg = EncodeLocation("nuremberg")
    regensburg = EncodeLocation("regensburg")
    salzburg = EncodeLocation("salzburg")
    command = EncodeLocation("command")
    msqc = EncodeLocation("msqc")
    anywhere = EncodeLocation("Anywhere")


START_LOCATIONS = (Loc.strasbourg, Loc.ulm, Loc.augsburg, Loc.munich,
                   Loc.nuremberg, Loc.regensburg, Loc.salzburg)
START_OPTIONS = tuple(enumerate(("스트라스부르", "울름", "아우크스부르크", "뮌헨",
                                 "뉘른베르크", "레겐스부르크", "잘츠부르크")))
