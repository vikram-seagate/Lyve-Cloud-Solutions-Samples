from enum import Enum

class Action(Enum):
    toDF      = 'dataframe'
    toInflux  = 'influxdb'
    toElastic = 'elastic'