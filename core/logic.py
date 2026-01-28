import pdfplumber
import re

# ==========================================
# === UTILIDADES (Traídas de tu script) ===
# ==========================================

MAPA_MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def es_numero_valido(texto):
    s = str(texto).replace('.', '').strip()
    return s.isdigit() or (s.startswith('-') and s[1:].isdigit())

def limpiar_numero(valor):
    if not valor: return 0
    s = str(valor).replace('.', '').strip()
    try:
        return int(s)
    except ValueError:
        return 0

def buscar_valor_en_fila(fila, codigo_buscado):
    # Tu lógica exacta de búsqueda en tablas
    fila = [str(x).strip() for x in fila if x is not None]
    for i, celda in enumerate(fila):
        if celda == codigo_buscado:
            for desplazamiento in range(1, 4):
                if i + desplazamiento < len(fila):
                    valor_candidato = fila[i + desplazamiento]
                    if es_numero_valido(valor_candidato):
                        return limpiar_numero(valor_candidato)
    return 0

def obtener_fecha_periodo(texto_pagina):
    match = re.search(r"PERIODO.*?(\d{4})(\d{2})\b", texto_pagina, re.IGNORECASE | re.DOTALL)
    if match:
        anio = int(match.group(1))
        mes_num = int(match.group(2))
        if 1 <= mes_num <= 12:
            return MAPA_MESES[mes_num], anio
    return "Desconocido", 0

# ==========================================
# === LÓGICA PRINCIPAL ADAPTADA A WEB ===
# ==========================================

def procesar_pdf_en_memoria(archivo_in_memory):
    """
    Recibe el archivo desde Django (RAM) y devuelve una lista de diccionarios con la data.
    """
    resultados = []
    rut_emisor = "S-R"
    nombre_emisor = "S-N"

    with pdfplumber.open(archivo_in_memory) as pdf:
        # 1. Intentar sacar datos del emisor de la primera página
        if len(pdf.pages) > 0:
            texto_portada = pdf.pages[0].extract_text() or ""
            match_nombre = re.search(r"Nombre del Emisor\s*[:]\s*(.+)", texto_portada, re.IGNORECASE)
            if match_nombre: nombre_emisor = match_nombre.group(1).strip()
            
            match_rut = re.search(r"RUT del Emisor\s*[:]\s*([\d\.-]+)", texto_portada, re.IGNORECASE)
            if match_rut: rut_emisor = match_rut.group(1).strip()

        # 2. Recorrer páginas (Igual que tu script original)
        for page in pdf.pages:
            texto_pagina = page.extract_text() or ""
            nombre_mes, anio_detectado = obtener_fecha_periodo(texto_pagina)
            
            # Inicializamos variables de tu lógica
            val_563 = 0; val_537 = 0; val_504 = 0; val_562 = 0
            val_151 = 0; val_062 = 0
            
            tablas = page.extract_tables()
            for tabla in tablas:
                for fila in tabla:
                    # Usamos tu función helper
                    v_563 = buscar_valor_en_fila(fila, "563")
                    if v_563: val_563 = v_563
                    
                    v_537 = buscar_valor_en_fila(fila, "537")
                    if v_537: val_537 = v_537
                    
                    v_504 = buscar_valor_en_fila(fila, "504")
                    if v_504: val_504 = v_504
                    
                    v_562 = buscar_valor_en_fila(fila, "562")
                    if v_562: val_562 = v_562
                    
                    v_151 = buscar_valor_en_fila(fila, "151")
                    if v_151: val_151 = v_151
                    
                    v_062 = buscar_valor_en_fila(fila, "062")
                    if v_062: val_062 = v_062

            # Solo procesamos si encontramos datos relevantes (tu lógica original)
            if (val_563 + val_537 + val_151 + val_062) > 0:
                # --- TUS CÁLCULOS MATEMÁTICOS ---
                credito_del_mes = val_537 - val_504
                if credito_del_mes < 0: credito_del_mes = 0
                
                compra_calculada = int(credito_del_mes / 0.19) if credito_del_mes > 0 else 0
                boletas_calculadas = int(val_151 / 0.145) if val_151 > 0 else 0 # Ojo: Revisar si la tasa 14.5% es fija o variable por año

                resultados.append({
                    "rut_emisor": rut_emisor,
                    "nombre_emisor": nombre_emisor,
                    "anio": anio_detectado,
                    "mes": nombre_mes,
                    "ingresos": val_563,
                    "compras_netas": compra_calculada,
                    "compras_exentas": val_562,
                    "boletas_honorarios": boletas_calculadas,
                    "ppm": val_062
                })

    return resultados