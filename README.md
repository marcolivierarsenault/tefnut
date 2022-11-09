# tefnut

<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Shu_with_feather.svg/640px-Shu_with_feather.svg.png' width='100'>

## Configuration 
  
### Weather API
  
<img src='https://openweathermap.org/themes/openweathermap/assets/img/logo_white_cropped.png' width='100'>

In order to do proper Humidity calculation, we need to know the outside temperature. To do so we use [OpenWeather API](https://openweathermap.org/api). Simply [register](https://home.openweathermap.org/users/sign_up) for the **FREE** access to weather data. You will need to add your API key in the configuration file. You also need to get your latitude and longitude value to get the appropriate weather information.

```toml
[WEATHER]
api_key = "123123123123123123123123123" # API Key 
lat = "45.50" # Montreal Latitude
lon = "-73.56" # Montreal Longitude
```

## Optional Configurations

### Remote Logging 

Tefnut is configure to be able to work with a remote logger (given that this is running on a Raspberry pi behind my furnase and I do not enjoy going there physically.) 


![Loki](https://grafana.com/static/img/logos/logo-loki.svg)

I you want remote logging, you need a [Loki server](https://grafana.com/oss/loki/). 

You can then add it to your configuration: 

```toml
[LOKI]
enable = true
name = "tefnut-dev"
url = "http://127.0.0.1:3100/loki/api/v1/push"
```

if you do not want any, you can delete all of this section or set it to false

```toml
[LOKI]
enable = false
```
