# Tefnut

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/546c9b7ee86f4d0eb5f7c7f1055ec072)](https://app.codacy.com/gh/marcolivierarsenault/tefnut?utm_source=github.com&utm_medium=referral&utm_content=marcolivierarsenault/tefnut&utm_campaign=Badge_Grade_Settings)

<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Shu_with_feather.svg/640px-Shu_with_feather.svg.png' width='100'>

`Tefnut (tfnwt) is a deity of moisture, moist air, dew and rain in Ancient Egyptian religion.` - [Wikipedia](https://en.wikipedia.org/wiki/Tefnut)

Tefnut is a control system to manage central humidificatior. Tefnut replace basic humidistat that only operate on a fix preset. It allows to use outdoor temperature which in cold climate, prevent condesation in windows. 

Instead, by using outside temperature, we are adjusting the desired setpoint automatically 


|Outside Temp (oC)|Target Humidity Level|
|---|---|
|<= -30|15%|
|<= -25|20%|
|<= -20|25%|
|<= -15|30%|
|<= -10|35%|
|<= 5|40%|
|> 5|45%|

## Limitation

This implementation of Tefnut is only compatible with:
* Humidistat that can be control via simple dry switches
* Access to hardware to control Humidificator switch (e.g. Raspberry Pi)
* Ecobee smart thermostat to reed house ambiant humidity level. 

Note: It is designed to be resonabily modular, so assuming you want to get humidity level from another source or you want to control Humidificator from something else than Rapberry pie, it should not be hard to replace in the source code. 

## Configuration 
 
* Installation and configuration [instruction available here](https://github.com/marcolivierarsenault/tefnut/wiki/Installation)
* Utilisation instruction can be [found here](https://github.com/marcolivierarsenault/tefnut/wiki/Usage)
