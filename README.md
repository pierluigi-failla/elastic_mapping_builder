# Elastic Mapping Builder

Convert a Python dict into an Elastic Mapping

Sometime could be helpful to create an [Elastic Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html) starting from a dictionary. This is exactly what [`ElasticMappingBuilder`](https://github.com/pierluigi-failla/elastic_mapping_builder/blob/master/mapper.py#L9) does.

Easy like:

    dct = {
        'timestamp': datetime.now(),
        'numerical': [1,2,3,4],
        'text': 'lorem ipsum, lore ipsum',
        'meta': {
            'meta1': 'lorem',
            'meta2': 423,
        }
    }

    mapper = ElasticMappingBuilder()
    elastic_mapping = mapper.convert(dct).get_mapping()

`elastic_mapping` now contains a dictionary that is compliant with Elastic Mapping, you can use it or change it without rewriting it from scratch. You can also override types conversion providing your own (defaults are defined [here](https://github.com/pierluigi-failla/elastic_mapping_builder/blob/master/mapper.py#L10)):

    my_types = [
        (datetime, {'type': 'date', 'format': 'yyyyMMdd'}),
    ]

    mapper = ElasticMappingBuilder(types=my_types)
    elastic_mapping = mapper.convert(dct).get_mapping()
    
and storing json files:

    mapper.to_json('mapping.json')
    
the example above will produce a `mapping.json` file containing:

    {
      "timestamp": {
        "type": "date",
        "format": "yyyyMMdd"
      },
      "numerical": {
        "type": "long"
      },
      "text": {
        "type": "text",
        "fields": {
          "keywords": {
            "type": "keyword"
          }
        }
      },
      "meta": {
        "properties": {
          "meta1": {
            "type": "text",
            "fields": {
              "keywords": {
               "type": "keyword"
              }
            }
          },
          "meta2": {
            "type": "long"
          }
        }
      }
    }

Enjoy!
