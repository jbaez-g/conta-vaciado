from django.urls import path
from core.views import (
    landing_view, dashboard_view, vaciado_view, 
    historial_view, descargar_proceso_view # <--- Nuevos nombres de vista
)

urlpatterns = [
    path('', landing_view, name='landing'),
    path('app/', dashboard_view, name='dashboard'),
    path('app/vaciado/', vaciado_view, name='vaciado'),
    path('app/historial/', historial_view, name='historial'),
    
    # Rutas actualizadas
    path('app/descargar/', descargar_proceso_view, name='descargar_excel'),
    path('app/descargar/<int:proceso_id>/', descargar_proceso_view, name='descargar_proceso'),
]