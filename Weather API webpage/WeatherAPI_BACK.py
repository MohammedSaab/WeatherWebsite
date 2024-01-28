from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
app = Flask(__name__, template_folder='templates', static_folder='static')
api_key = os.getenv('API_KEY')

# Convert temperature
def kelvin_to_fahrenheit(kelvin):
    return round((kelvin - 273.15) * 9/5 + 32)

# Capitalize city name
def capitalize_city(city):
    return city.title()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input from the form
        city = request.form.get('city', '')
        if city:
            formatted_city = capitalize_city(city)
            # Make an API call with the user-input city
            weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={formatted_city}&appid={api_key}'
            forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={formatted_city}&appid={api_key}'

            try:
                # Get current weather data
                response_weather = requests.get(weather_url)
                response_weather.raise_for_status()
                data_weather = response_weather.json()

                # Get forecast data
                response_forecast = requests.get(forecast_url)
                response_forecast.raise_for_status()
                data_forecast = response_forecast.json()

                # Check if 'weather' key exists and has data
                if 'weather' in data_weather and data_weather['weather']:
                    sky_condition = data_weather['weather'][0]['description'].title()
                else:
                    sky_condition = 'Not available'

                # Convert current temperature to Fahrenheit
                temperature_fahrenheit = kelvin_to_fahrenheit(data_weather['main']['temp'])
                humidity = data_weather.get('main',{}).get('humidity',None) 
                month_mapping = {
                '01': 'January',
                '02': 'February',
                '03': 'March',
                '04': 'April',
                '05': 'May',
                '06': 'June',
                '07': 'July',
                '08': 'August',
                '09': 'September',
                '10': 'October',
                '11': 'November',
                '12': 'December'
                }
                forecast_data = []
                for entry in data_forecast['list'][:4]:
                    date_before = entry['dt_txt'].split("-")[1:3]  # Extract date without timestamps
                    date_list = [element.split()[0] for element in date_before]
                    month_number = date_list[0]
                    day_number = date_list[1]
                    if month_number in month_mapping:
                        month_name = month_mapping[month_number]
                        date = f'{month_name} {day_number}'
                    temperature = kelvin_to_fahrenheit(entry['main']['temp'])
                    description = entry['weather'][0]['description'].title()
                    humidity = entry['main']['humidity']
                    forecast_data.append({'date': date, 'temperature': temperature, 'description': description, 'humidity': humidity})

                # Pass the forecast data to the template
                return render_template('index.html', temperature_fahrenheit=temperature_fahrenheit, city=formatted_city, sky_condition=sky_condition, humidity=humidity, forecast_data=forecast_data)
            except requests.exceptions.RequestException as e:
                return render_template('error.html', error_message=str(e))

    # If it's a GET request or there was an error, render the form
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
