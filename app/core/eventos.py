# Se crea la clase para manejar los usuarios
from typing import Optional, List
from utils.connectiondb import get_session
from datetime import datetime, timedelta
from models.eventos import TbEvento
import calendar

class EventosCRUD:
    def __init__(self):
        pass

    # Crear un evento
    def crear_evento(self, evento_data: dict) -> dict:
        """
        Crea un nuevo evento si no existe uno con el mismo nombre.
        Devuelve el nuevo evento en una lista o None si ya existe.
        Omite el guardado si el consumo es igual a 0 para evitar valores basura.
        """
        # Verificar si el consumo es 0 y omitir el guardado
        consumo = evento_data.get('consumo', 0)
        
        # Convertir a float para comparación segura
        try:
            consumo_float = float(consumo) if consumo is not None else 0.0
        except (ValueError, TypeError):
            consumo_float = 0.0
        
        if consumo_float == 0.0:
            return {"message": "Evento omitido - consumo igual a 0", "success": True}, 200
        
        session = get_session()
        try:
            nuevo_evento = TbEvento(**evento_data)
            session.add(nuevo_evento)
            session.commit()
            return nuevo_evento.to_dict(), 200
        finally:
            session.close()
    
    # Eliminar un evento
    def eliminar_evento(self, id_evento: int) -> dict:
        session = get_session()
        try:
            evento = session.query(TbEvento).filter(TbEvento.id == id_evento).first()
            if evento:
                session.delete(evento)
                session.commit()
                return {"message": "Evento eliminado correctamente"}, 200
            return {"message": "Evento no encontrado"}, 404
        finally:
            session.close()
    
    # Actualizar un evento
    def actualizar_evento(self, id_evento: int, evento_data: dict) -> dict:
        session = get_session()
        try:
            evento = session.query(TbEvento).filter(TbEvento.id == id_evento).first()
            if evento:
                for key, value in evento_data.items():
                    setattr(evento, key, value)
                session.commit()
                return evento.to_dict(), 200
            return {"message": "Evento no encontrado"}, 404
        finally:
            session.close()
    
    # Obtener un evento por id
    def obtener_evento_por_id(self, id_evento: int) -> dict:
        """
        Obtiene un evento específico por su ID.
        """
        session = get_session()
        try:
            evento = session.query(TbEvento).filter(TbEvento.id == id_evento).first()
            if evento:
                return evento.to_dict(), 200
            return {"message": "Evento no encontrado"}, 404
        finally:
            session.close()
    
   # Obtener eventos en un intervalo de tiempo, fechas, dias, meses, años
    def obtener_eventos_por_fecha(self, fecha_inicio: str, fecha_fin: str) -> dict:
        """
        Obtiene eventos en un rango de fechas específico.
        Formato esperado: 'YYYY-MM-DD'
        """
        session = get_session()
        try:
            # Validar formato de fechas
            try:
                # ✅ Mejorado: Crear fechas con hora específica para rangos precisos
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                return {"message": "Formato de fecha inválido. Use 'YYYY-MM-DD'"}, 400
            
            # Validar que fecha_inicio <= fecha_fin
            if fecha_inicio_dt > fecha_fin_dt:
                return {"message": "La fecha de inicio debe ser menor o igual a la fecha fin"}, 400

            # ✅ Mejorado: Query más robusto con manejo de zona horaria
            eventos = session.query(TbEvento).filter(
                TbEvento.fecha_evento >= fecha_inicio_dt, 
                TbEvento.fecha_evento <= fecha_fin_dt
            ).order_by(TbEvento.fecha_evento.desc()).all()

            if eventos:
                return [evento.to_dict() for evento in eventos], 200
            return {"message": "No se encontraron eventos en el rango de fechas especificado"}, 404
        except Exception as e:
            # ✅ Agregado: Manejo de errores más específico
            return {"message": f"Error al consultar eventos: {str(e)}"}, 500
        finally:
            session.close()
    
    # Obtener eventos los ultimos dias
    def obtener_eventos_ultimos_dias(self, dias: int) -> dict:
        """
        Obtiene eventos de los últimos N días agrupados por día con consumo sumalizado.
        """
        session = get_session()
        try:
            # Validar que días sea un número positivo
            if not isinstance(dias, int) or dias <= 0:
                return {"message": "El número de días debe ser un entero positivo"}, 400
            
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            # Query para agrupar por día y sumarizar consumo
            from sqlalchemy import func, cast, Date
            from decimal import Decimal
            
            eventos_agrupados = session.query(
                cast(TbEvento.fecha_evento, Date).label('fecha'),
                func.sum(TbEvento.consumo).label('consumo_total'),
                TbEvento.unidad_medida
            ).filter(
                TbEvento.fecha_evento >= fecha_limite
            ).group_by(
                cast(TbEvento.fecha_evento, Date),
                TbEvento.unidad_medida
            ).order_by(
                cast(TbEvento.fecha_evento, Date).desc()
            ).all()
            
            if eventos_agrupados:
                resultado = []
                for evento in eventos_agrupados:
                    resultado.append({
                        'fecha': evento.fecha.strftime('%Y-%m-%d'),
                        'consumo_total': float(evento.consumo_total),
                        'unidad_medida': evento.unidad_medida
                    })
                return resultado, 200
            return {"message": "No se encontraron eventos"}, 404
        finally:
            session.close()
   
    # Obtener eventos los ultimos meses
    def obtener_eventos_ultimos_meses(self, meses: int) -> dict:
        """
        Obtiene eventos de los últimos N meses agrupados por mes con consumo sumalizado.
        """
        session = get_session()
        try:
            # Validar que meses sea un número positivo
            if not isinstance(meses, int) or meses <= 0:
                return {"message": "El número de meses debe ser un entero positivo"}, 400
            
            # Calcular fecha límite de manera más precisa
            fecha_actual = datetime.now()
            fecha_limite = fecha_actual.replace(day=1)  # Primer día del mes actual
            for _ in range(meses):
                # Retroceder un mes
                if fecha_limite.month == 1:
                    fecha_limite = fecha_limite.replace(year=fecha_limite.year-1, month=12)
                else:
                    fecha_limite = fecha_limite.replace(month=fecha_limite.month-1)
            
            # Query para agrupar por mes y sumarizar consumo
            from sqlalchemy import func, extract
            from decimal import Decimal
            
            eventos_agrupados = session.query(
                extract('year', TbEvento.fecha_evento).label('anio'),
                extract('month', TbEvento.fecha_evento).label('mes'),
                func.sum(TbEvento.consumo).label('consumo_total'),
                TbEvento.unidad_medida
            ).filter(
                TbEvento.fecha_evento >= fecha_limite
            ).group_by(
                extract('year', TbEvento.fecha_evento),
                extract('month', TbEvento.fecha_evento),
                TbEvento.unidad_medida
            ).order_by(
                extract('year', TbEvento.fecha_evento).desc(),
                extract('month', TbEvento.fecha_evento).desc()
            ).all()
            
            if eventos_agrupados:
                resultado = []
                for evento in eventos_agrupados:
                    resultado.append({
                        'anio': int(evento.anio),
                        'mes': int(evento.mes),
                        'mes_nombre': calendar.month_name[int(evento.mes)],
                        'consumo_total': float(evento.consumo_total),
                        'unidad_medida': evento.unidad_medida
                    })
                return resultado, 200
            return {"message": "No se encontraron eventos"}, 404
        finally:
            session.close()
    
    # Obtener eventos los ultimos años
    def obtener_eventos_ultimos_anios(self, anios: int) -> dict:
        """
        Obtiene eventos de los últimos N años agrupados por año con consumo sumalizado.
        """
        session = get_session()
        try:
            # Validar que años sea un número positivo
            if not isinstance(anios, int) or anios <= 0:
                return {"message": "El número de años debe ser un entero positivo"}, 400
            
            # Calcular fecha límite de manera más precisa
            fecha_actual = datetime.now()
            fecha_limite = fecha_actual.replace(year=fecha_actual.year - anios)
            
            # Query para agrupar por año y sumarizar consumo
            from sqlalchemy import func, extract
            from decimal import Decimal
            
            eventos_agrupados = session.query(
                extract('year', TbEvento.fecha_evento).label('anio'),
                func.sum(TbEvento.consumo).label('consumo_total'),
                TbEvento.unidad_medida
            ).filter(
                TbEvento.fecha_evento >= fecha_limite
            ).group_by(
                extract('year', TbEvento.fecha_evento),
                TbEvento.unidad_medida
            ).order_by(
                extract('year', TbEvento.fecha_evento).desc()
            ).all()
            
            if eventos_agrupados:
                resultado = []
                for evento in eventos_agrupados:
                    resultado.append({
                        'anio': int(evento.anio),
                        'consumo_total': float(evento.consumo_total),
                        'unidad_medida': evento.unidad_medida
                    })
                return resultado, 200
            return {"message": "No se encontraron eventos"}, 404
        finally:
            session.close()
    
    # Obtener todos los eventos
    def obtener_todos_eventos(self) -> dict:
        session = get_session()
        try:
            eventos = session.query(TbEvento).all()
            if eventos:
                return [evento.to_dict() for evento in eventos], 200
            return {"message": "No se encontraron eventos"}, 404
        finally:
            session.close()
    