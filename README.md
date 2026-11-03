# Open-Meteo SDK Schema Files

[![Test](https://github.com/open-meteo/sdk/actions/workflows/test.yml/badge.svg)](https://github.com/open-meteo/sdk/actions/workflows/test.yml) [![GitHub version](https://badge.fury.io/gh/open-meteo%2Fsdk.svg)](https://badge.fury.io/gh/open-meteo%2Fsdk) [![npm version](https://badge.fury.io/js/@openmeteo%2Fsdk.svg)](https://www.npmjs.com/package/@openmeteo/sdk) [![PyPI version](https://badge.fury.io/py/openmeteo-sdk.svg)](https://pypi.org/project/openmeteo-sdk/)

The Open-Meteo weather API uses FlatBuffers to encode API responses efficiently. The compiled schema files for various programming languages can be found in this repository.

The biggest advantage of FlatBuffers is that large floating point arrays can be encoded directly instead of expensive transformation to JSON ASCII. Especially for historical weather data processing is significantly faster. But also for displaying a regular weather forecast on low-power devices, binary data encoding saves energy.

The FlatBuffers schema definition can be found in the [./flatbuffers](./flatbuffers) directory. Only non-breaking changes are accepted. Binary compatibility is ensured. Every change will be announced in new release following semantic versioning.

The compiled schema files do not contain any code to perform HTTP calls. They are intent to be used by developers to build client libraries.

More information on how to use the compiled schema files can be found in the directories for each programming language
- [Swift](./swift/) via Swift Package Manager
- [Python](./python/) via PIP
- [TypeScript / JavaScript](./ts/) via NPM
- [Java](./java/) via Maven Central
- [C#](./csharp/openmeteo_sdk/)

Not all programming languages are supported yet. It is a time-intensive process to validate all languages. Please open an issue ticket to ask for an additional language and/or package distribution system.

## Usage
Open-Meteo offers various APIs. Each API endpoint is using different FlatBuffers schemas to encode its API response. This enables strict typing. E.g. Weather data APIs offer offers different variables while the Geocoding API returns a different structure. Per default, the Open-Meteo API returns JSON, but specifying `&format=flatbuffers` in the URL return FlatBuffers encoded data.

Depending on the programming language, you can use an HTTP client to fetch all data and decode the response according to each API endpoint. The following API response schema files are available:
- [Weather, Marine, Ensemble, Flood and Climate API](./flatbuffers/weather_api.fbs): Used for forecast and historical data
- Elevation API: Not yet available
- Geocoding API: Not yet available


## Structure
Each response contains data for one location and one weather model. If multiple locations are requested, multiple ApiResponses will be returned as an array using `size-prefixed` encoding (see below).

### WeatherApiResponse
The main `WeatherApiResponse` structure contains
- `latitude` & `longitude` float: Coordinate of the weather model grid-cell
- `elevation` float: Terrain elevation of the requested coordinates
- `generation_time_milliseconds` float
- `location_id` int64: Identifier of a location
- `model` [Model](#Model): Name of weather model as an enumeration
- `utc_offset_seconds` int32: Timezone offset from GMT time in seconds. e.g. `3600`
- `timezone` string: Timezone name like `Europe/Berlin`
- `timezone_abbreviation` string: Abbreviation like `CET`
- `current` [VariablesWithTime](#VariablesWithTime): All variables requested with `&current=`
- `daily` [VariablesWithTime](#VariablesWithTime): All variables requested with `&daily=`
- `hourly` [VariablesWithTime](#VariablesWithTime): All variables requested with `&hourly=`
- `minutely_15` [VariablesWithTime](#VariablesWithTime): All variables requested with `&minutely_15=`
- `monthly` [VariablesWithMonth](#VariablesWithMonth): All variables requested with `&monthly=`
- `weekly` [VariablesWithTime](#VariablesWithTime): All variables requested with `&weekly=`

### VariablesWithTime
All `hourly` or `daily` weather variables are grouped into the class `VariablesWithTime`. It contains the start and end time as well as the interval.

Attributes:
- `time` int64: Unix timestamp of the first value in GMT
- `time_end` int64: The last timestamp that is not included in the time-interval. Therefore one step after the last included timestep.
- `interval` int32:  The number of seconds for each step. For hourly data this is `3600 seconds` and for daily data `86400 seconds`.
- `variables` [[VariableWithValues](#VariableWithValues)]: An array of weather variables

Timestamps always use unixtime in seconds. Time is always in GMT! If you want to display local time again, you can use the attribute `utc_offset_seconds` from the response structure

### VariablesWithMonth
All `monthly` weather variables are grouped into the class `VariablesWithMonth`. It contains the first year and month as well as the number of steps.

Attributes:
- `year` int16: The first year of the returned data. E.g. `2025`.
- `month` int8: The first month. From 1 to 12.
- `count` int32: The number of step for monthly data. 24 means 2 years of data is returned.
- `variables` [[VariableWithValues](#VariableWithValues)]: An array of weather variables

### VariableWithValues
Each weather variable is accompanied by meta data like the name of the weather variable or unit.

Attributes:
- `variable` [Variable](#Variable): An enumeration of the weather variable. E.g. `temperature`
- `unit` [Unit](#Unit): Which unit is used for the result. E.g. `celsius`
- `value` float: For `current` values, data is stored in this field
- `values` [float]: Any other time-series data is stored as a floating point array here
- `values_int64` [int64]: The variables `sunrise`, `sunset`, `moonrise`, and `moonset` use this field to store Unix timestamps in seconds. `INT64_MAX` (`9223372036854775807`) is the missing timestamp sentinel when an event does not occur during the local calendar day.
- `altitude` int16: The altitude of the given variable. E.g `2` for temperature on 2 meters or `10` for wind speed on 10 meters
- `aggregation` [Aggregation](#Aggregation): The kind of aggregation for daily variables like `minimum`, `mean` or `maximum`
- `pressure_level` int16: If a weather variable in the upper atmosphere is requested, this field contains the pressure level in hectopascal. E.g. `850` for 850 hPa.
- `depth` int16: For soil variables this defined the upper limit. E.g. `7` in `soil_moisture_7_to_28`
- `depth_to` int16: The lower limit. E.g. `28` in `soil_moisture_7_to_28`
- `ensemble_member` int16: For ensemble data, the member of each ensemble is set here. `0` is mostly the control run.
- `previous_day` int16: Number of days before the current date to include
- `probability` [Probability](#Probability): Probability threshold for ensemble probability variables

In Python, the raw sentinel can be converted to `NaT` before working with the timestamps in pandas:

```python
import numpy as np
import pandas as pd

missing_int64 = np.iinfo(np.int64).max

raw = variable.ValuesInt64AsNumpy()
timestamps = pd.to_datetime(
    pd.Series(raw).mask(raw == missing_int64),
    unit="s",
    utc=True,
)
```

### Model
The `Model` enumeration contains all available models like `icon_global` or `best_match`.

Depending on the programming language you will have to decode the model to a useable string. E.g. for Python

```python
from openmeteo_sdk import Model

def model_to_name(code):
    """convert Model to name"""
    for name, value in Model.Model.__dict__.items():
        if value == code:
            return name
    return None

print(response.Model()) # 1
print(model_to_name(result.Model())) # "best_match"
```

### Variable
The `Variable` enumeration contains all available variables like `temperature` or `wind_speed`. Please note that the altitude is not included in the variable name. `temperature_2m` is encoded as `variable=temperature` and `altitude=2`.

### Unit
The `Unit` enumeration contains all available units like `celsius` or `metre_per_second`.

### Aggregation
The `Aggregation` enumeration contains all aggregations for daily variables like `minimum` or `maximum`.

### Probability
The `Probability` enumeration contains probability thresholds for ensemble probability variables like `gt5` (greater than 5) or `lt0` (less than 0).

```

Note: The values for `model`, `variable`, `unit` and `aggregation` are encoded into enumerations which use integers instead of strings. Only `timezone` and `timezone_abbreviation` are actual strings that are encoded in the binary API response.

# License
MIT