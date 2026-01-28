import pandas as pd
import io
import re
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .logic import procesar_pdf_en_memoria
from .models import ProcesoVaciado, DetalleF29  # <--- AQUÍ ESTÁ EL CAMBIO CLAVE

def limpiar_nombre_archivo(texto):
    return re.sub(r'[\\/*?:"<>|]', "", texto).strip()

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required
def vaciado_view(request):
    resultados_visuales = []
    error = None
    
    if request.method == 'POST' and request.FILES.get('archivo_pdf'):
        archivo = request.FILES['archivo_pdf']
        nombre_archivo = archivo.name
        
        try:
            datos_lista = procesar_pdf_en_memoria(archivo)
            
            if not datos_lista:
                error = "No se encontraron datos legibles."
            else:
                # 1. CREAR EL PADRE
                primer_dato = datos_lista[0]
                nuevo_proceso = ProcesoVaciado.objects.create(
                    user=request.user,
                    nombre_archivo_original=nombre_archivo,
                    rut_cliente=primer_dato['rut_emisor'],
                    nombre_cliente=primer_dato['nombre_emisor'],
                    cantidad_periodos=len(datos_lista)
                )
                
                # 2. CREAR LOS HIJOS
                for data in datos_lista:
                    DetalleF29.objects.create(
                        proceso=nuevo_proceso,
                        anio=data['anio'],
                        mes=data['mes'],
                        ingresos=data['ingresos'],
                        compras_netas=data['compras_netas'],
                        compras_exentas=data['compras_exentas'],
                        boletas_honorarios=data['boletas_honorarios'],
                        ppm=data['ppm']
                    )
                    
                    data_web = data.copy()
                    campos = ['ingresos', 'compras_netas', 'compras_exentas', 'boletas_honorarios', 'ppm']
                    for c in campos:
                        data_web[c] = f"{data_web[c]:,}".replace(",", ".")
                    resultados_visuales.append(data_web)

                request.session['ultimo_proceso_id'] = nuevo_proceso.id

        except Exception as e:
            error = f"Error técnico: {str(e)}"

    return render(request, 'vaciado.html', { 
        'resultados': resultados_visuales, 
        'error': error,
    })

@login_required
def historial_view(request):
    mis_procesos = ProcesoVaciado.objects.filter(user=request.user).order_by('-fecha_creacion')
    return render(request, 'historial.html', {'historial': mis_procesos})

@login_required
def descargar_proceso_view(request, proceso_id=None):
    if proceso_id is None:
        proceso_id = request.session.get('ultimo_proceso_id')

    if not proceso_id:
        return HttpResponse("No hay datos para descargar.", status=404)

    proceso = get_object_or_404(ProcesoVaciado, id=proceso_id, user=request.user)
    detalles = proceso.detalles.all().order_by('anio', 'mes')

    datos_excel = []
    for d in detalles:
        datos_excel.append({
            "Año": d.anio,
            "Mes": d.mes,
            "Ingresos": d.ingresos,
            "Compras Netas": d.compras_netas,
            "Compras Exentas": d.compras_exentas,
            "Boletas Honorarios": d.boletas_honorarios,
            "PPM": d.ppm
        })
    
    df = pd.DataFrame(datos_excel)
    
    rut_limpio = limpiar_nombre_archivo(proceso.rut_cliente)
    nombre_limpio = limpiar_nombre_archivo(proceso.nombre_cliente)
    fecha_str = proceso.fecha_creacion.strftime("%d-%m-%Y")
    nombre_archivo = f"Consolidado - {rut_limpio} {nombre_limpio} ({fecha_str}).xlsx"

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Detalle')
        workbook = writer.book
        worksheet = writer.sheets['Detalle']
        fmt_contabilidad = '_-$* #,##0_-;-$* #,##0_-;_-* "-"_-;_-@_-'
        
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=3, max_col=7):
            for cell in row:
                cell.number_format = fmt_contabilidad
        
        for col in worksheet.columns:
            try:
                worksheet.column_dimensions[col[0].column_letter].width = 15
            except: pass

    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response