"""
Formateador de respuestas para mejorar la presentación visual
Convierte texto plano en HTML con formato atractivo
"""

import re
from typing import Dict, List
from app.ui.styles import theme_manager


class ResponseFormatter:
    """
    🎨 FORMATEADOR UNIVERSAL DE RESPUESTAS V2.0

    CARACTERÍSTICAS MEJORADAS:
    - Formateo automático inteligente de CUALQUIER texto
    - Detección automática del tipo de contenido
    - Estilos consistentes y profesionales
    - Soporte completo para markdown y texto plano
    - Formateo especializado por contexto
    """

    def __init__(self):
        # 🎯 USAR THEMEMANAGER CENTRALIZADO para estilos
        self.styles = theme_manager.get_response_formatter_styles()

        # 🆕 PATRONES DE DETECCIÓN AUTOMÁTICA
        self.content_patterns = {
            'student_list': [r'\d+\.\s+[A-ZÁÉÍÓÚÑ\s]+', r'CURP:', r'📋', r'🎓'],
            'help_content': [r'\*\*.*?\*\*', r'¿.*\?', r'💡', r'📚', r'ℹ️'],
            'statistics': [r'\d+\s+(alumnos?|estudiantes?)', r'Total:', r'📊', r'📈'],
            'error_message': [r'❌', r'Error', r'No se pudo', r'⚠️'],
            'success_message': [r'✅', r'Éxito', r'Generado', r'Completado'],
            'constancia_info': [r'constancia', r'PDF', r'generado', r'archivo'],
            'greeting': [r'¡Hola!', r'Bienvenido', r'Es un gusto', r'saludarte']
        }

    def format_response(self, text: str, response_type: str = "auto") -> str:
        """
        🎨 FORMATEA CUALQUIER RESPUESTA CON DETECCIÓN AUTOMÁTICA

        Args:
            text: Texto a formatear
            response_type: Tipo de respuesta ("auto" para detección automática)

        Returns:
            HTML formateado profesionalmente
        """
        try:
            # 🔍 DETECCIÓN AUTOMÁTICA SI NO SE ESPECIFICA TIPO
            if response_type == "auto" or response_type == "general":
                response_type = self._detect_content_type(text)

            # 🎯 APLICAR FORMATEO ESPECÍFICO
            if response_type == "help":
                return self._format_help_response(text)
            elif response_type == "data" or response_type == "student_list":
                return self._format_data_response(text)
            elif response_type == "error":
                return self._format_error_response(text)
            elif response_type == "success":
                return self._format_success_response(text)
            elif response_type == "statistics":
                return self._format_statistics_response(text)
            elif response_type == "greeting":
                return self._format_greeting_response(text)
            else:
                return self._format_enhanced_general_response(text)

        except Exception as e:
            # En caso de error, aplicar formateo básico
            return self._format_enhanced_general_response(text)

    def _detect_content_type(self, text: str) -> str:
        """🔍 DETECTA AUTOMÁTICAMENTE EL TIPO DE CONTENIDO"""
        # Contar coincidencias para cada tipo
        type_scores = {}

        for content_type, patterns in self.content_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            type_scores[content_type] = score

        # Retornar el tipo con mayor puntuación
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type

        return "general"

    def _format_help_response(self, text: str) -> str:
        """Formatea respuestas de ayuda usando configuración centralizada"""
        # Convertir listas con viñetas
        text = self._convert_bullet_lists(text)

        # Convertir títulos con **
        text = self._convert_bold_titles(text)

        # 🎯 USAR CONFIGURACIÓN CENTRALIZADA PARA WRAPPERS
        if self.styles.get('enable_wrappers', False):
            return f"""
            <div style="{self.styles['help_border']}
                        padding: {self.styles['wrapper_padding']};
                        margin: {self.styles['wrapper_margin']};">
                <div style="font-size: {self.styles['font_size']}; line-height: {self.styles['line_height']};">
                    {text}
                </div>
            </div>
            """
        else:
            # 🎯 SIN WRAPPER - SOLO TEXTO LIMPIO
            return text

    def _format_data_response(self, text: str) -> str:
        """📊 FORMATEA RESPUESTAS CON DATOS usando configuración centralizada"""
        # 🔧 APLICAR FORMATEO MARKDOWN COMPLETO
        text = self._convert_bold_titles(text)
        text = self._convert_bullet_lists(text)
        text = self._enhance_emojis(text)
        text = self._highlight_important_info(text)
        text = self._highlight_numbers(text)

        # 🎯 USAR CONFIGURACIÓN CENTRALIZADA PARA WRAPPERS
        if self.styles.get('enable_wrappers', False):
            return f"""
            <div style="{self.styles['data_border']}
                        padding: {self.styles['wrapper_padding']};
                        margin: {self.styles['wrapper_margin']};">
                <div style="font-size: {self.styles['font_size']}; line-height: {self.styles['line_height']};">
                    {text}
                </div>
            </div>
            """
        else:
            # 🎯 SIN WRAPPER - SOLO TEXTO LIMPIO (DataDisplayManager ya formatea bien)
            return text

    def _format_error_response(self, text: str) -> str:
        """Formatea respuestas de error usando configuración centralizada"""
        # 🎯 USAR CONFIGURACIÓN CENTRALIZADA PARA WRAPPERS
        if self.styles.get('enable_wrappers', False):
            return f"""
            <div style="{self.styles['error_border']}
                        padding: {self.styles['wrapper_padding']};
                        margin: {self.styles['wrapper_margin']};">
                <div style="font-size: {self.styles['font_size']}; line-height: {self.styles['line_height']};">
                    {text}
                </div>
            </div>
            """
        else:
            return text

    def _format_success_response(self, text: str) -> str:
        """Formatea respuestas de éxito usando configuración centralizada"""
        # 🎯 USAR CONFIGURACIÓN CENTRALIZADA PARA WRAPPERS
        if self.styles.get('enable_wrappers', False):
            return f"""
            <div style="{self.styles['success_border']}
                        padding: {self.styles['wrapper_padding']};
                        margin: {self.styles['wrapper_margin']};">
                <div style="font-size: {self.styles['font_size']}; line-height: {self.styles['line_height']};">
                    {text}
                </div>
            </div>
            """
        else:
            return text

    def _format_enhanced_general_response(self, text: str) -> str:
        """🎨 FORMATEA RESPUESTAS GENERALES usando configuración centralizada"""
        # Aplicar todas las mejoras de formateo
        text = self._convert_bullet_lists(text)
        text = self._convert_bold_titles(text)
        text = self._enhance_emojis(text)
        text = self._improve_spacing(text)
        text = self._highlight_important_info(text)

        # 🎯 USAR CONFIGURACIÓN CENTRALIZADA PARA WRAPPERS
        if self.styles.get('enable_wrappers', False):
            return f"""
            <div style="font-size: {self.styles['font_size']};
                        line-height: {self.styles['line_height']};
                        padding: {self.styles['wrapper_padding']};
                        margin: {self.styles['wrapper_margin']};">
                {text}
            </div>
            """
        else:
            return text

    def _format_statistics_response(self, text: str) -> str:
        """📊 FORMATEA RESPUESTAS CON ESTADÍSTICAS usando configuración centralizada"""
        text = self._highlight_numbers(text)
        text = self._convert_bullet_lists(text)
        text = self._enhance_emojis(text)

        # 🎯 USAR CONFIGURACIÓN CENTRALIZADA PARA WRAPPERS
        if self.styles.get('enable_wrappers', False):
            return f"""
            <div style="{self.styles['data_border']}
                        padding: {self.styles['wrapper_padding']};
                        margin: {self.styles['wrapper_margin']};">
                <div style="font-size: {self.styles['font_size']}; line-height: {self.styles['line_height']};">
                    {text}
                </div>
            </div>
            """
        else:
            return text

    def _format_greeting_response(self, text: str) -> str:
        """👋 FORMATEA MENSAJES DE BIENVENIDA usando configuración centralizada"""
        text = self._convert_bullet_lists(text)
        text = self._convert_bold_titles(text)
        text = self._enhance_emojis(text)
        text = self._improve_spacing(text)

        # 🎯 USAR CONFIGURACIÓN CENTRALIZADA PARA WRAPPERS
        if self.styles.get('enable_wrappers', False):
            return f"""
            <div style="{self.styles['success_border']}
                        padding: {self.styles['wrapper_padding']};
                        margin: {self.styles['wrapper_margin']};">
                <div style="font-size: {self.styles['font_size']}; line-height: {self.styles['line_height']};">
                    {text}
                </div>
            </div>
            """
        else:
            return text



    def _convert_bullet_lists(self, text: str) -> str:
        """Convierte listas con * en HTML SIN sobrescribir colores del ChatBubble"""
        lines = text.split('\n')
        in_list = False
        result = []

        for line in lines:
            stripped = line.strip()
            # 🎯 NO CONVERTIR LÍNEAS QUE YA TIENEN FORMATO DE NÚMERO (ej: **1.** NOMBRE)
            if stripped.startswith('*') and not re.match(r'\*\*\d+\.\*\*', stripped):
                if not in_list:
                    result.append('<ul style="margin: 15px 0; padding-left: 25px; list-style-type: none;">')
                    in_list = True

                item_text = stripped[1:].strip()
                # 🎯 SIN colores específicos - usar inherit para respetar ChatBubble
                item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
                result.append(f'<li style="margin: 8px 0; position: relative; padding-left: 20px;"><span style="position: absolute; left: 0; opacity: 0.7;">•</span>{item_text}</li>')
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append(line)

        if in_list:
            result.append('</ul>')

        return '\n'.join(result)

    def _convert_bold_titles(self, text: str) -> str:
        """Convierte texto en **negrita** a HTML simple SIN estilos inline problemáticos"""
        # 🎯 USAR <strong> EN LUGAR DE <h4> PARA EVITAR SALTOS DE LÍNEA
        text = re.sub(
            r'\*\*(.*?)\*\*',
            r'<strong>\1</strong>',
            text
        )
        return text

    def _highlight_numbers(self, text: str) -> str:
        """Resalta números importantes usando estilos centralizados"""
        # 🎯 USAR ESTILOS CENTRALIZADOS
        text = re.sub(
            r'\b(\d{2,})\b',
            rf'<span style="{self.styles["number_highlight"]} font-weight: bold;">\1</span>',
            text
        )
        return text

    def _enhance_emojis(self, text: str) -> str:
        """Mejora la presentación de emojis SIN sobrescribir colores del ChatBubble"""
        # 🎯 Solo mejorar tamaño y espaciado, SIN colores específicos
        emojis = ['🔍', '📊', '📄', '🔄', '💬', '🆘', '✅', '❌', '⚠️']

        for emoji in emojis:
            if emoji in text:
                text = text.replace(
                    emoji,
                    f'<span style="font-size: 18px; margin-right: 5px;">{emoji}</span>'
                )
        return text

    def _improve_spacing(self, text: str) -> str:
        """🎨 MEJORA EL ESPACIADO DEL TEXTO"""
        # Agregar espacios después de puntos seguidos de mayúscula
        text = re.sub(r'\.([A-ZÁÉÍÓÚÑ])', r'. \1', text)

        # Mejorar espaciado alrededor de emojis
        text = re.sub(r'([📊📋🎓🔍👥💡✅❌⚠️])([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])([📊📋🎓🔍👥💡✅❌⚠️])', r'\1 \2', text)

        # Limpiar espacios múltiples
        text = re.sub(r'\s+', ' ', text)

        return text

    def _highlight_important_info(self, text: str) -> str:
        """🎯 RESALTA INFORMACIÓN IMPORTANTE"""
        # 🔧 SIMPLIFICAR RESALTADO DE CURPs (sin CSS complejo)
        text = re.sub(
            r'\b([A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d)\b',
            r'<code>\1</code>',
            text
        )

        # 🔧 SIMPLIFICAR RESALTADO DE MATRÍCULAS (sin CSS complejo)
        text = re.sub(
            r'\b([A-Z]{4}-\d{6}-[A-Z0-9]{3})\b',
            r'<code>\1</code>',
            text
        )

        # Resaltar grados y grupos
        text = re.sub(
            r'\b(\d+°\s+[A-Z])\b',
            r'<span style="font-weight: bold; opacity: 0.9;">\1</span>',
            text
        )

        return text

    @staticmethod
    def format_any_response(text: str) -> str:
        """
        🎨 MÉTODO ESTÁTICO UNIVERSAL PARA FORMATEAR CUALQUIER RESPUESTA

        Este método puede ser llamado desde cualquier parte del sistema
        para garantizar formateo consistente de todas las respuestas.

        Args:
            text: Cualquier texto a formatear

        Returns:
            HTML formateado profesionalmente
        """
        formatter = ResponseFormatter()
        return formatter.format_response(text, "auto")

    def format_student_list(self, students: List[Dict], title: str = "Resultados") -> str:
        """Formatea lista de estudiantes de manera atractiva"""
        if not students:
            return '<div style="color: #6c757d; font-style: italic;">No se encontraron estudiantes.</div>'

        html = f"""
        <div style="background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin: 15px 0;">
            <h3 style="color: #495057; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                📋 {title} ({len(students)} estudiante{'s' if len(students) != 1 else ''})
            </h3>
            <div style="display: grid; gap: 10px;">
        """

        for i, student in enumerate(students, 1):
            nombre = student.get('nombre', 'N/A')
            grado = student.get('grado', 'N/A')
            grupo = student.get('grupo', 'N/A')
            turno = student.get('turno', 'N/A')

            html += f"""
            <div style="background-color: white; border: 1px solid #dee2e6; border-radius: 8px;
                        padding: 12px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #212529; font-size: 16px;">{i}. {nombre}</strong>
                    <div style="color: #6c757d; font-size: 14px; margin-top: 4px;">
                        {grado}° {grupo} - {turno}
                    </div>
                </div>
                <div style="color: #007bff; font-size: 12px;">
                    ID: {student.get('id', 'N/A')}
                </div>
            </div>
            """

        html += """
            </div>
        </div>
        """

        return html
