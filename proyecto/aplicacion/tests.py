from django.test import TestCase
from .models import YourModel  # Reemplaza 'YourModel' con el nombre de tu modelo

class YourModelTests(TestCase):

    def setUp(self):
        # Configura los datos necesarios para las pruebas
        YourModel.objects.create(field1='value1', field2='value2')  # Ajusta los campos según tu modelo

    def test_model_str(self):
        # Prueba que el método __str__ de tu modelo funcione correctamente
        model_instance = YourModel.objects.get(field1='value1')
        self.assertEqual(str(model_instance), 'Expected String Representation')  # Ajusta según tu modelo

    def test_model_field(self):
        # Prueba que un campo específico tenga el valor esperado
        model_instance = YourModel.objects.get(field1='value1')
        self.assertEqual(model_instance.field2, 'value2')  # Ajusta según tu modelo