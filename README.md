[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/marcolivierarsenault/tefnut?label=latest%20version)](https://github.com/marcolivierarsenault/tefnut/tags) [![tefnut testing](https://github.com/marcolivierarsenault/tefnut/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/marcolivierarsenault/tefnut/actions/workflows/python-app.yml) ![Python](https://img.shields.io/badge/python-3.13-blue) [![codecov](https://codecov.io/gh/marcolivierarsenault/tefnut/branch/main/graph/badge.svg?token=WCYXQXQVO3)](https://codecov.io/gh/marcolivierarsenault/tefnut) [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/marcolivierarsenault/tefnut/graphs/commit-activity)

# Tefnut

<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Shu_with_feather.svg/640px-Shu_with_feather.svg.png' width='100'>

`Tefnut (tfnwt) is a deity of moisture, moist air, dew and rain in Ancient Egyptian religion.` - [Wikipedia](https://en.wikipedia.org/wiki/Tefnut)

Tefnut is a control system to manage central humidificatior. Tefnut replace basic humidistat that only operate on a fix preset. It allows to use outdoor temperature which in cold climate, prevent condesation in windows.

Instead, by using outside temperature, we are adjusting the desired setpoint automatically

| Outside Temp (oC) | Target Humidity Level |
| ----------------- | --------------------- |
| <= -30            | 15%                   |
| <= -25            | 20%                   |
| <= -20            | 25%                   |
| <= -15            | 30%                   |
| <= -10            | 35%                   |
| <= 5              | 40%                   |
| > 5               | 45%                   |

## Limitation

This implementation of Tefnut is only compatible with:

- Humidistat that can be control via simple dry switches
- Access to hardware to control Humidifier switch (e.g. Raspberry Pi)
- Ecobee smart thermostat to reed house ambiant humidity level.

Note: It is designed to be resonabily modular, so assuming you want to get humidity level from another source or you want to control Humidifier from something else than Rapberry pie, it should not be hard to replace in the source code.

## Configuration

- Installation and configuration [instruction available here](https://github.com/marcolivierarsenault/tefnut/wiki/Installation)
- Utilisation instruction can be [found here](https://github.com/marcolivierarsenault/tefnut/wiki/Usage)
