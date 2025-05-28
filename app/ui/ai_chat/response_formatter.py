"""
Formateador de respuestas para mejorar la presentación visual
Convierte texto plano en HTML con formato atractivo
"""

import re
from typing import Dict, List
from app.ui.styles import theme_manager


class ResponseFormatter:
    """
    Formateador inteligente de respuestas para mejorar la presentación visual

    CARACTERÍSTICAS:
    - Convierte markdown a HTML
    - Aplica estilos según el tipo de contenido
    - Mejora listas, títulos, y elementos especiales
    - Mantiene consistencia visual
    """

    def __init__(self):
        # 🎯 USAR THEMEMANAGER CENTRALIZADO para estilos
        self.styles = theme_manager.get_response_formatter_styles()

    def format_response(self, text: str, response_type: str = "general") -> str:
        """
        Formatea una respuesta según su tipo

        Args:
            text: Texto a formatear
            response_type: Tipo de respuesta (help, data, error, success)

        Returns:
            HTML formateado
        """
        try:
            # Aplicar formateo específico según el tipo
            if response_type == "help":
                return self._format_help_response(text)
            elif response_type == "data":
                return self._format_data_response(text)
            elif response_type == "error":
                return self._format_error_response(text)
            elif response_type == "success":
                return self._format_success_response(text)
            else:
                return self._format_general_response(text)

        except Exception as e:
            # En caso de error, devolver texto original
            return text

    def _format_help_response(self, text: str) -> str:
        """Formatea respuestas de ayuda SIN sobrescribir colores del ChatBubble"""
        # Convertir listas con viñetas
        text = self._convert_bullet_lists(text)

        # Convertir títulos con **
        text = self._convert_bold_titles(text)

        # 🎯 USAR ESTILOS CENTRALIZADOS
        formatted = f"""
        <div style="{self.styles['help_border']}
                    padding-left: 15px;
                    margin: 10px 0;">
            <div style="font-size: 16px; line-height: 1.8;">
                {text}
            </div>
        </div>
        """

        return formatted

    def _format_data_response(self, text: str) -> str:
        """Formatea respuestas con datos SIN sobrescribir colores"""
        # Convertir listas
        text = self._convert_bullet_lists(text)

        # Resaltar números y estadísticas
        text = self._highlight_numbers(text)

        # 🎯 USAR ESTILOS CENTRALIZADOS
        formatted = f"""
        <div style="{self.styles['data_border']}
                    padding-left: 15px; margin: 10px 0;">
            <div style="font-size: 15px; line-height: 1.5;">
                {text}
            </div>
        </div>
        """

        return formatted

    def _format_error_response(self, text: str) -> str:
        """Formatea respuestas de error SIN sobrescribir colores"""
        # 🎯 USAR ESTILOS CENTRALIZADOS
        formatted = f"""
        <div style="{self.styles['error_border']}
                    padding-left: 15px; margin: 10px 0;">
            <div style="font-size: 15px; opacity: 0.9;">
                {text}
            </div>
        </div>
        """

        return formatted

    def _format_success_response(self, text: str) -> str:
        """Formatea respuestas de éxito usando estilos centralizados"""
        # 🎯 USAR ESTILOS CENTRALIZADOS
        formatted = f"""
        <div style="{self.styles['success_border']}
                    padding-left: 15px; margin: 10px 0;">
            <div style="font-size: 15px; opacity: 0.9;">
                {text}
            </div>
        </div>
        """

        return formatted

    def _format_general_response(self, text: str) -> str:
        """Formatea respuestas generales"""
        # Aplicar formateo básico
        text = self._convert_bullet_lists(text)
        text = self._convert_bold_titles(text)
        text = self._enhance_emojis(text)

        return f'<div style="font-size: 15px; line-height: 1.6;">{text}</div>'

    def _convert_bullet_lists(self, text: str) -> str:
        """Convierte listas con * en HTML SIN sobrescribir colores del ChatBubble"""
        lines = text.split('\n')
        in_list = False
        result = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('*'):
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
        """Convierte texto en **negrita** a títulos HTML SIN sobrescribir colores"""
        # 🎯 SIN colores específicos - usar inherit para respetar ChatBubble
        text = re.sub(
            r'\*\*(.*?)\*\*',
            r'<h4 style="margin: 15px 0 10px 0; font-size: 17px; font-weight: bold; opacity: 0.9;">\1</h4>',
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
