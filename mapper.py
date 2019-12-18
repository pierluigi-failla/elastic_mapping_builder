# -*- coding: utf-8 -*-

import logging
import json

from datetime import datetime


class ElasticMappingBuilder(object):
    _types = [
        (int,        {'type': 'long'}),
        (float,      {'type': 'float'}),
        (str,        {'type': 'text', 'fields': {'keywords': {'type': 'keyword'}}}),
        (bool,       {'type': 'boolean'}),
        (datetime,   {'type': 'date', 'format': 'yyyy-MM-dd HH:mm:ss'}),
        (type(None), {'type': 'NULL'})
    ]
    
    @staticmethod
    def _base_type(item):
        for _t, _v in ElasticMappingBuilder._types:
            if type(item) == _t:
                return _v
        logging.warn(f'unknown type: {type(item)} for value: {item}')
        return {'[ERROR]': f'unknown type: {type(item)} for value: {item}'}
    
    @staticmethod
    def _process(dct):
        """ Navigate the dict and build the mapping."""
        mapping = {}
        for k, v in dct.items():
            if type(v) == dict:
                mapping[k] = {'properties': ElasticMappingBuilder._process(v)}
                continue
            if type(v) == set or type(v) == list:
                if len(v) == 0:
                    mapping[k] = ElasticMappingBuilder._base_type(None)
                    continue
                if type(v[0]) == dict:
                    mapping[k] = {'properties': ElasticMappingBuilder._process(v[0])}
                else:
                    mapping[k] = ElasticMappingBuilder._base_type(v[0])
                continue
            mapping[k] = ElasticMappingBuilder._base_type(v)
        return mapping
    
    def __init__(self, types=[]):
        """Convert a dict into an Elastic Mapping

        if needed types conversion can be overridden by providing an updated list 
        of conversions (take a look to `ElasticMappingBuilder._types`)
        
        Example:
        
        >>> my_types = [
        >>>     (datetime, {'type': 'date', 'format': 'yyyyMMdd'}),
        >>> ]
        >>> 
        >>> dct = {
        >>>     'timestamp': datetime.now(),
        >>>     'numerical': [1,2,3,4],
        >>>     'text': 'lorem ipsum, lore ipsum',
        >>>     'meta': {
        >>>         'meta1': 'lorem',
        >>>         'meta2': 423,
        >>>     }
        >>> }
        >>> 
        >>> mapper = ElasticMappingBuilder(types=my_types)
        >>> elastic_mapping = mapper.convert(dct).get_mapping()
        >>> mapper.to_json('mapping.json')
        
        store: 
        
        >>> {
        >>>   "timestamp": {
        >>>     "type": "date",
        >>>     "format": "yyyyMMdd"
        >>>   },
        >>>   "numerical": {
        >>>     "type": "long"
        >>>   },
        >>>   "text": {
        >>>     "type": "text",
        >>>     "fields": {
        >>>       "keywords": {
        >>>         "type": "keyword"
        >>>       }
        >>>     }
        >>>   },
        >>>   "meta": {
        >>>     "properties": {
        >>>       "meta1": {
        >>>         "type": "text",
        >>>         "fields": {
        >>>           "keywords": {
        >>>            "type": "keyword"
        >>>           }
        >>>         }
        >>>       },
        >>>       "meta2": {
        >>>         "type": "long"
        >>>       }
        >>>     }
        >>>   }
        >>> }
        
        in mapping.json
        
        """
        if len(types) > 0:
             ElasticMappingBuilder._types = types + ElasticMappingBuilder._types
        self._mapping = {}
    
    def convert(self, dct):
        assert type(dct) == dict, f'type mismatch, expected `dict` got `{type(dct)}`'
        self._mapping = ElasticMappingBuilder._process(dct)
        logging.info(f'dict has been converted')
        return self
    
    def to_json(self, filename):
        if self._mapping is None:
            logging.warn(f'no mapping available, nothing has been saved')
            return self
        json.dump(self._mapping, open(filename, 'w'), indent=2)
    
    def get_mapping(self):
        if self._mapping is None:
            logging.warn(f'no mapping available')
        return self._mapping
