# Se crea la clase para manejar los niveles de agua
from typing import Optional, List
from utils.connectiondb import get_session
from datetime import datetime, timedelta
from models.niveles_agua import TbNivelAgua
from sqlalchemy import func, cast, Date


class NivelAguaCRUD:
    def __init__(self):
        pass

    def crear_nivel_agua(self, nivel_data: dict) -> tuple:
        """
        Crear un nuevo registro de nivel de agua.
        
        Args:
            nivel_data: Diccionario con los datos del nivel de agua
            
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            # Crear nueva instancia
            nuevo_nivel = TbNivelAgua(
                distancia=nivel_data.get('distancia'),
                desnivel=nivel_data.get('desnivel'),
                bomba=nivel_data.get('bomba'),
                compuerta=nivel_data.get('compuerta'),
                nivel_estado=nivel_data.get('nivel_estado'),
                porcentaje_agua=nivel_data.get('porcentaje_agua'),
                fecha=nivel_data.get('fecha', datetime.now())
            )
            
            # Guardar en la base de datos
            session.add(nuevo_nivel)
            session.commit()
            session.refresh(nuevo_nivel)
            
            return {
                "success": True,
                "message": "Nivel de agua creado exitosamente",
                "data": nuevo_nivel.to_dict()
            }, 201
            
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "error": f"Error creando nivel de agua: {str(e)}"
            }, 500
        finally:
            session.close()

    def obtener_nivel_agua(self, id_nivel: int) -> tuple:
        """
        Obtener un nivel de agua por ID.
        
        Args:
            id_nivel: ID del nivel de agua
            
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            nivel = session.query(TbNivelAgua).filter(TbNivelAgua.id_nivel == id_nivel).first()
            
            if nivel:
                return {
                    "success": True,
                    "data": nivel.to_dict()
                }, 200
            else:
                return {
                    "success": False,
                    "error": "Nivel de agua no encontrado"
                }, 404
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo nivel de agua: {str(e)}"
            }, 500
        finally:
            session.close()

    def obtener_todos_niveles_agua(self, limit: int = 100, offset: int = 0) -> tuple:
        """
        Obtener todos los niveles de agua con paginación.
        
        Args:
            limit: Número máximo de registros a retornar
            offset: Número de registros a saltar
            
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            niveles = session.query(TbNivelAgua)\
                .order_by(TbNivelAgua.fecha.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            total = session.query(TbNivelAgua).count()
            
            return {
                "success": True,
                "data": [nivel.to_dict() for nivel in niveles],
                "total": total,
                "limit": limit,
                "offset": offset
            }, 200
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo niveles de agua: {str(e)}"
            }, 500
        finally:
            session.close()

    def actualizar_nivel_agua(self, id_nivel: int, nivel_data: dict) -> tuple:
        """
        Actualizar un nivel de agua existente.
        
        Args:
            id_nivel: ID del nivel de agua a actualizar
            nivel_data: Diccionario con los datos a actualizar
            
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            nivel = session.query(TbNivelAgua).filter(TbNivelAgua.id_nivel == id_nivel).first()
            
            if not nivel:
                return {
                    "success": False,
                    "error": "Nivel de agua no encontrado"
                }, 404
            
            # Actualizar campos
            for key, value in nivel_data.items():
                if hasattr(nivel, key):
                    setattr(nivel, key, value)
            
            session.commit()
            
            return {
                "success": True,
                "message": "Nivel de agua actualizado exitosamente",
                "data": nivel.to_dict()
            }, 200
            
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "error": f"Error actualizando nivel de agua: {str(e)}"
            }, 500
        finally:
            session.close()

    def eliminar_nivel_agua(self, id_nivel: int) -> tuple:
        """
        Eliminar un nivel de agua.
        
        Args:
            id_nivel: ID del nivel de agua a eliminar
            
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            nivel = session.query(TbNivelAgua).filter(TbNivelAgua.id_nivel == id_nivel).first()
            
            if not nivel:
                return {
                    "success": False,
                    "error": "Nivel de agua no encontrado"
                }, 404
            
            session.delete(nivel)
            session.commit()
            
            return {
                "success": True,
                "message": "Nivel de agua eliminado exitosamente"
            }, 200
            
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "error": f"Error eliminando nivel de agua: {str(e)}"
            }, 500
        finally:
            session.close()

    def obtener_niveles_por_fecha(self, fecha_inicio: datetime, fecha_fin: datetime) -> tuple:
        """
        Obtener niveles de agua por rango de fechas.
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            niveles = session.query(TbNivelAgua)\
                .filter(TbNivelAgua.fecha >= fecha_inicio)\
                .filter(TbNivelAgua.fecha <= fecha_fin)\
                .order_by(TbNivelAgua.fecha.desc())\
                .all()
            
            return {
                "success": True,
                "data": [nivel.to_dict() for nivel in niveles],
                "total": len(niveles),
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat()
            }, 200
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo niveles por fecha: {str(e)}"
            }, 500
        finally:
            session.close()

    def obtener_ultimo_nivel(self) -> tuple:
        """
        Obtener el último registro de nivel de agua.
        
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            ultimo_nivel = session.query(TbNivelAgua)\
                .order_by(TbNivelAgua.fecha.desc())\
                .first()
            
            if ultimo_nivel:
                return {
                    "success": True,
                    "data": ultimo_nivel.to_dict()
                }, 200
            else:
                return {
                    "success": False,
                    "error": "No hay registros de nivel de agua"
                }, 404
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo último nivel: {str(e)}"
            }, 500
        finally:
            session.close()

    def obtener_estadisticas_nivel(self, dias: int = 7) -> tuple:
        """
        Obtener estadísticas de niveles de agua.
        
        Args:
            dias: Número de días para calcular estadísticas
            
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            # Obtener datos del período
            niveles = session.query(TbNivelAgua)\
                .filter(TbNivelAgua.fecha >= fecha_limite)\
                .all()
            
            if not niveles:
                return {
                    "success": False,
                    "error": "No hay datos para el período especificado"
                }, 404
            
            # Calcular estadísticas
            distancias = [float(n.distancia) for n in niveles if n.distancia]
            desniveles = [n for n in niveles if n.desnivel == 'True']
            criticos = [n for n in niveles if n.nivel_estado == 'CRITICO']
            
            estadisticas = {
                "periodo_dias": dias,
                "total_registros": len(niveles),
                "promedio_distancia": round(sum(distancias) / len(distancias), 2) if distancias else 0,
                "max_distancia": round(max(distancias), 2) if distancias else 0,
                "min_distancia": round(min(distancias), 2) if distancias else 0,
                "alertas_desnivel": len(desniveles),
                "niveles_criticos": len(criticos),
                "ultima_lectura": niveles[0].to_dict() if niveles else None
            }
            
            return {
                "success": True,
                "data": estadisticas
            }, 200
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calculando estadísticas: {str(e)}"
            }, 500
        finally:
            session.close()

    def obtener_ultimo_nivel_agua(self) -> tuple:
        """
        Obtener el último registro de nivel de agua registrado.
        
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            ultimo_nivel = session.query(TbNivelAgua)\
                .order_by(TbNivelAgua.fecha.desc())\
                .first()
            
            if ultimo_nivel:
                return {
                    "success": True,
                    "data": ultimo_nivel.to_dict()
                }, 200
            else:
                return {
                    "success": False,
                    "error": "No hay registros de nivel de agua"
                }, 404
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo último nivel de agua: {str(e)}"
            }, 500
        finally:
            session.close()

    def obtener_ultimo_nivel_con_historial(self) -> tuple:
        """
        Obtener el último nivel de agua con historial de los últimos 7 días.
        
        Returns:
            tuple: (response_dict, status_code)
        """
        session = get_session()
        try:
            # Obtener el último registro
            ultimo_nivel = session.query(TbNivelAgua)\
                .order_by(TbNivelAgua.fecha.desc())\
                .first()
            
            if not ultimo_nivel:
                return {
                    "success": False,
                    "error": "No hay registros de nivel de agua"
                }, 404
            
            # Calcular fecha de hace 7 días (sin incluir el día actual)
            fecha_limite = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
            
            # Obtener la última lectura de cada día de los últimos 7 días (sin incluir el día actual)
            # Usamos una subconsulta para obtener el ID máximo de cada día
            
            # Subconsulta para obtener la fecha y el ID máximo de cada día
            subquery = session.query(
                cast(TbNivelAgua.fecha, Date).label('fecha_dia'),
                func.max(TbNivelAgua.id_nivel).label('max_id')
            ).filter(
                TbNivelAgua.fecha >= fecha_limite,
                TbNivelAgua.fecha < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ).group_by(
                cast(TbNivelAgua.fecha, Date)
            ).subquery()
            
            # Obtener los registros correspondientes a los IDs máximos de cada día
            historial = session.query(TbNivelAgua)\
                .join(subquery, TbNivelAgua.id_nivel == subquery.c.max_id)\
                .order_by(TbNivelAgua.fecha.desc())\
                .all()
            
            # Convertir historial a lista de diccionarios
            historial_data = [nivel.to_dict() for nivel in historial]
            
            # Preparar respuesta con interpretación
            ultimo_data = ultimo_nivel.to_dict()
            interpretacion = self._interpretar_nivel_agua(ultimo_data)
            
            response_data = {
                "success": True,
                "data": ultimo_data,
                "interpretacion": interpretacion,
                "historial_7_dias": historial_data
            }
            
            return response_data, 200
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo último nivel con historial: {str(e)}"
            }, 500
        finally:
            session.close()

    def _interpretar_nivel_agua(self, water_data: dict) -> dict:
        """
        Interpretar los datos del nivel de agua y proporcionar recomendaciones.
        
        Args:
            water_data: Diccionario con datos del nivel de agua
            
        Returns:
            dict: Interpretación y recomendaciones
        """
        distancia = water_data.get('distancia', 0)
        desnivel = water_data.get('desnivel', 'False') == 'True'
        bomba = water_data.get('bomba', 'False') == 'True'
        compuerta = water_data.get('compuerta', 'False') == 'True'
        nivel_estado = water_data.get('nivel_estado', 'UNKNOWN')
        
        # Determinar nivel y descripción
        if desnivel:
            nivel = "Crítico"
            descripcion = "Se ha detectado un desnivel en el sistema de agua"
            recomendacion = "Verificar inmediatamente el sistema y activar protocolos de emergencia"
            color = "red"
        elif nivel_estado == "CRITICO":
            nivel = "Crítico"
            descripcion = "El nivel de agua está en estado crítico"
            recomendacion = "Activar sistemas de drenaje y verificar la causa"
            color = "red"
        elif nivel_estado == "ALTO":
            nivel = "Alto"
            descripcion = "El nivel de agua está por encima de lo normal"
            recomendacion = "Considerar abrir compuertas de drenaje"
            color = "orange"
        elif nivel_estado == "NORMAL":
            nivel = "Normal"
            descripcion = "El nivel de agua está dentro de los parámetros normales"
            recomendacion = "No se requiere acción inmediata"
            color = "green"
        elif nivel_estado == "BAJO":
            nivel = "Bajo"
            descripcion = "El nivel de agua está por debajo de lo normal"
            recomendacion = "Verificar suministro de agua"
            color = "yellow"
        elif nivel_estado == "MUY_BAJO":
            nivel = "Muy Bajo"
            descripcion = "El nivel de agua está muy por debajo de lo normal"
            recomendacion = "Activar sistemas de bombeo y verificar suministro"
            color = "red"
        else:
            nivel = "Desconocido"
            descripcion = "No se puede determinar el estado del nivel de agua"
            recomendacion = "Verificar el funcionamiento del sensor"
            color = "gray"
        
        # Información adicional sobre dispositivos
        dispositivos = {
            "bomba": {
                "estado": "Activa" if bomba else "Inactiva",
                "descripcion": "Bomba de drenaje está funcionando" if bomba else "Bomba de drenaje está detenida"
            },
            "compuerta": {
                "estado": "Abierta" if compuerta else "Cerrada",
                "descripcion": "Compuerta de control está abierta" if compuerta else "Compuerta de control está cerrada"
            }
        }
        
        return {
            "nivel": nivel,
            "descripcion": descripcion,
            "recomendacion": recomendacion,
            "color": color,
            "dispositivos": dispositivos,
            "medicion": {
                "distancia": f"{distancia} cm",
                "interpretacion": "Distancia desde el sensor hasta la superficie del agua"
            }
        } 