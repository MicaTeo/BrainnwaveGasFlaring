import overpy

api = overpy.Overpass()

feature_query = """
      [out:json][timeout:100];
      (
        node["amenity"="bar"](55.818170,-3.4446024,56.014024,-3.0795530);
        way["amenity"="bar"](55.818170,-3.4446024,56.014024,-3.0795530);
      );
      out center;
      >;
      """

result = api.query(feature_query)

#
print(result.nodes[0].tags)
print(result.nodes[0].lat)
print(result.nodes[0].lon)
