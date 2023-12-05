import io
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from django_filters.rest_framework import FilterSet, filters
from rest_framework import status
from rest_framework.response import Response

from recipes import models

def create_shopping_cart(ingredients_cart):
    """Функция для формирования списка покупок."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        "attachment; filename='shopping_cart.pdf'"
    )
    pdfmetrics.registerFont(
        TTFont('Arial', 'data/arial.ttf', 'UTF-8')
    )
    buffer = io.BytesIO()
    pdf_file = canvas.Canvas(buffer)
    pdf_file.setFont('Arial', 24)
    pdf_file.drawString(200, 800, 'Список покупок.')
    pdf_file.setFont('Arial', 14)
    from_bottom = 750
    for number, ingredient in enumerate(ingredients_cart, start=1):
        pdf_file.drawString(
            50,
            from_bottom,
            f"{number}. {ingredient['ingredient__name']}: "
            f"{ingredient['ingredient_value']} "
            f"{ingredient['ingredient__measurement_unit']}.",
        )
        from_bottom -= 20
        if from_bottom <= 50:
            from_bottom = 800
            pdf_file.showPage()
            pdf_file.setFont('Arial', 14)
    pdf_file.showPage()
    pdf_file.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def add_or_del_obj(pk, request, param, serializer_context):
    obj = get_object_or_404(models.Recipe, pk=pk)
    obj_bool = param.filter(pk=obj.pk).exists()
    if request.method == 'DELETE' and obj_bool:
        param.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == 'POST' and not obj_bool:
        param.add(obj)
        serializer = serializer_context(
            obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)