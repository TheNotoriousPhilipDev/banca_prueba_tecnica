import boto3
import joblib
import pandas as pd
import base64
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Registro

# Configuramos cliente S3
s3 = boto3.client('s3', region_name='us-east-1',
                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

# Se carga el modelo preentrenado (quemado en el código)
model = joblib.load('iris_model.joblib')


def predict_from_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']

        try:
            # Leer archivo Excel desde el request
            file_data = excel_file.read()

            # Convertir a Base64
            encoded_data = base64.b64encode(file_data).decode('utf-8')

            # Subir el archivo codificado a S3 como texto
            s3.put_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=excel_file.name,
                Body=encoded_data,
                ContentType='text/plain'
            )

            # Procesar predicción
            buffer = BytesIO(base64.b64decode(encoded_data))
            df = pd.read_excel(buffer)

            # Validar columnas necesarias
            required_columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
            if set(required_columns).issubset(df.columns):
                X = df[required_columns]
                predictions = model.predict(X)
                df['Prediction'] = predictions

                # Generar URL del archivo (para referencia)
                file_url = f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{excel_file.name}"
                file_size = excel_file.size / 1024  # Tamaño en KB

                # Guardar información en la base de datos
                Registro.objects.create(
                    nombre_archivo=excel_file.name,
                    url_archivo=file_url,
                    peso_archivo=f"{file_size:.2f} KB",
                )

                return render(request, 'results.html', {
                    'table': df.to_html(index=False),
                    'registros': Registro.objects.all(),
                })
            else:
                return render(request, 'upload.html', {
                    'error': f'El archivo Excel debe contener las columnas: {required_columns}',
                    'registros': Registro.objects.all(),
                })
        except Exception as e:
            return render(request, 'upload.html', {
                'error': f'Ocurrió un error al procesar el archivo: {str(e)}',
                'registros': Registro.objects.all(),
            })
    return render(request, 'upload.html', {
        'registros': Registro.objects.all(),
    })


def eliminar_registro(request, registro_id):
    """
    Vista para eliminar un registro de la base de datos y el archivo correspondiente en S3.
    """
    if request.method == 'POST':
        registro = get_object_or_404(Registro, id=registro_id)

        try:
            # Eliminar archivo en S3
            s3.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=registro.nombre_archivo)
        except Exception as e:
            print(f"Error al eliminar archivo en S3: {str(e)}")

        # Eliminar el registro de SQLite
        registro.delete()
        return redirect('/')


def ver_prediccion(request, registro_id):
    try:
        # Obtener el registro desde la base de datos
        registro = get_object_or_404(Registro, id=registro_id)

        # Descargar el archivo codificado desde S3
        response = s3.get_object(Bucket=settings.AWS_BUCKET_NAME, Key=registro.nombre_archivo)
        encoded_data = response['Body'].read().decode('utf-8')

        # Decodificar de Base64 a binario
        decoded_data = base64.b64decode(encoded_data)

        # Leer el archivo Excel desde el buffer
        buffer = BytesIO(decoded_data)
        df = pd.read_excel(buffer)

        required_columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
        if set(required_columns).issubset(df.columns):
            x = df[required_columns]
            predictions = model.predict(x)

            # Agregar la columna de predicciones
            df['Prediction'] = predictions

            # Convertir el DataFrame a una tabla HTML
            table_html = df.to_html(index=False)

            # Renderizar la plantilla con la tabla HTML y otros datos
            return render(request, 'results.html', {
                'table': table_html,
                'registros': Registro.objects.all(),
            })
        else:
            return render(request, 'upload.html', {
                'error': f"El archivo no contiene las columnas requeridas: {required_columns}",
                'registros': Registro.objects.all(),
            })
    except Exception as e:
        return render(request, 'upload.html', {
            'error': f"Error al procesar el archivo: {str(e)}",
            'registros': Registro.objects.all(),
        })
