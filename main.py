import units
import units.abc

unit_dict = {"infantry": units.Infantry, "vehicle": units.Vehicle}
RED = 0xFF0000
red_HQ = units.Headquarters(RED, unit_dict)
red_unit = red_HQ.create_unit("infantry", (0, 0))
