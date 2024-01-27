from collections import defaultdict

problems = []
mp_by_route = defaultdict(list)

with arcpy.da.SearchCursor("Milepost", ["RouteId", "Measure", "MilepostNumber", "OID@"], where_clause="MilepostType=3") as mps:
    for mp in mps:
        mp_by_route[mp[0]].append(mp[1:])

for route, mps in mp_by_route.items():
    last_mp_num = None
    for mp in sorted(mps):
        if last_mp_num is None:
            last_mp_num = mp[1]
        elif mp[1] <= last_mp_num:
            problems.append(str(mp[2]))

arcpy.management.SelectLayerByAttribute("Milepost", selection_type="NEW_SELECTION", where_clause="ObjectId in ({})".format(",".join(problems)))

    
