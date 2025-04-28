from flask import Flask, render_template, request, redirect
import requests
from datetime import datetime, date
from googletrans import Translator
import boto3
from botocore.exceptions import ClientError
import json


def get_secret():

    secret_name = "my-app/api-key"
    region_name = "eu-north-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

app = Flask(__name__)


secrets = get_secret()
API_KEY = secrets.get('API_KEY')
API_LINK = secrets.get('API_LINK')

@app.route('/', methods=['GET', 'POST'])
def get_days_weather():
    if request.method == 'POST':
        location = request.form.get('user-text')
    else:
        location = 'Israel'  # Default location if form is not submitted
        print("Hello")

    api_url = (
        f'{API_LINK}/{location.capitalize()}/next7days?unitGroup=metric&include=days%2Ccurrent&key='
        f'{API_KEY}&contentType=json')

    response = requests.get(api_url)

    translator = Translator()

    status_code = response.status_code

    if status_code != 200:
        return redirect('notFound')
    else:
        data = response.json()

        full_location = translator.translate(data['resolvedAddress']).text

        weather_data = []  # Initialize the list outside the loop
        current_day = []

        for day in data['days']:
            if datetime.strptime(day['datetime'], '%Y-%m-%d') == datetime.strptime(str(date.today()), "%Y-%m-%d"):
                current_day_data = {
                    'day': datetime.strptime(day['datetime'], '%Y-%m-%d').strftime('%a'),  # Day of the week
                    'date_time': day['datetime'],
                    'temp': int(day['temp']),
                    'temp_max': day['tempmax'],
                    'temp_min': day['tempmin'],
                    'humidity': day['humidity'],
                    'wind_speed': day['windspeed'],
                    'icon': day['icon']
                }
                current_day.append(current_day_data)

            elif datetime.strptime(day['datetime'], '%Y-%m-%d') != datetime.strptime(str(date.today()), "%Y-%m-%d"):
                days_data = {
                    'day': datetime.strptime(day['datetime'], '%Y-%m-%d').strftime('%a'),  # Day of the week
                    'date_time': day['datetime'],
                    'temp': int(day['temp']),
                    'icon': day['icon']

                }
                weather_data.append(days_data)  # Append data for each day
        return render_template("index.html", days_weather=weather_data, current_day_weather=current_day,
                               location=full_location)

@app.route('/notFound')
def not_found_redirect():
    return render_template("not_found.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)