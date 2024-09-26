import os
import json
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import pickle

# TODO Load the model
model_path = os.path.join(settings.BASE_DIR, 'ML_model/banglore_home_prices_model.pickle')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# TODO Load the column names
columns_path = os.path.join(settings.BASE_DIR, 'ML_model/columns.json')
with open(columns_path, 'r') as f:
    data_columns = json.load(f)['data_columns']

# TODO Extract the location columns
location_columns = data_columns[3:]


def index(request):
    if request.method == 'POST':
        sqft = request.POST.get('sqft')
        bhk = request.POST.get('uiBHK')
        bath = request.POST.get('uibath')
        location = request.POST.get('uilocations')

        print(sqft, bhk, bath, location)

        if not sqft or not bhk or not bath or not location:
            return JsonResponse({'error': 'Missing input data'}, status=400)

        try:
            sqft = float(sqft)
            bhk = int(bhk)
            bath = int(bath)
        except ValueError:
            return JsonResponse({'error': 'Invalid input data'}, status=400)

        try:
            # TODO Create the feature vector
            x = np.zeros(len(data_columns))
            x[0] = sqft
            x[1] = bath
            x[2] = bhk
            if location in location_columns:
                loc_index = data_columns.index(location)
                x[loc_index] = 1

            # TODO Predict the price
            pred = model.predict([x])[0]
            pred = round(pred, 3)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        print(pred)

        return render(request, 'data.html', {'predicted_price': pred})

    return render(request, 'data.html')


def get_location(request):
    json_file_path = os.path.join(settings.BASE_DIR, 'ML_model/columns.json')

    with open(json_file_path, 'r') as f:
        data = json.load(f)
        locations = data['data_columns'][3:]  # Skip the first three columns: "total_sqft", "bath", "bhk"

    return JsonResponse({'locations': locations})
