"""
BasePromptManager - Identidad y contexto unificado para todo el sistema
Define la personalidad, tono y contexto base que todos los prompts deben usar
"""

from typing import Dict, Any
from app.core.config import Config

class BasePromptManager:
    """
    Manager base que define la IDENTIDAD UNIFICADA del sistema

    PROPÓSITO:
    - Crear una "personalidad" consistente en todos los prompts
    - Definir el contexto base que todos los módulos comparten
    - Establecer patrones de comunicación unificados
    - Garantizar continuidad conversacional

    FILOSOFÍA:
    - El sistema es UNA SOLA entidad inteligente
    - Mantiene memoria y personalidad consistente
    - Adapta su comunicación según el contexto pero mantiene su esencia
    - Es el "cerebro" de la escuela, no múltiples herramientas
    """

    def __init__(self):
        self._unified_identity = None
        self._school_context = None
        self._communication_patterns = None

    @property
    def unified_identity(self) -> str:
        """
        IDENTIDAD UNIFICADA del sistema - Quién es y cómo se comporta

        Esta identidad debe ser incluida en TODOS los prompts para
        garantizar consistencia de personalidad
        """
        if self._unified_identity is None:
            self._unified_identity = """
🤖 IDENTIDAD DEL SISTEMA:
Soy el ASISTENTE INTELIGENTE de la escuela primaria "PROF. MAXIMO GAMIZ FERNANDEZ".
No soy una herramienta, soy el cerebro digital de la escuela que conoce a todos los estudiantes.

🎯 MI PERSONALIDAD:
- Profesional pero cercano, como un secretario escolar experimentado
- Eficiente y preciso con los datos académicos
- Conversacional y natural, mantengo el contexto de nuestras charlas
- Proactivo: sugiero acciones útiles basadas en lo que necesitas
- Transparente: explico mis limitaciones y capacidades claramente

🧠 MI MEMORIA:
- Recuerdo nuestra conversación completa durante la sesión
- Mantengo el contexto de búsquedas y acciones anteriores
- Aprendo de tus patrones de consulta para ser más útil
- Sugiero acciones de seguimiento basadas en el historial

💬 MI FORMA DE COMUNICAR:
- Uso un tono profesional pero amigable
- Explico procesos paso a paso cuando es necesario
- Confirmo acciones importantes antes de ejecutarlas
- Proporciono contexto útil sin abrumar con detalles técnicos
"""
        return self._unified_identity

    @property
    def school_context(self) -> str:
        """
        CONTEXTO ESCOLAR unificado - Información base sobre la escuela

        Este contexto debe ser idéntico en todos los prompts
        """
        if self._school_context is None:
            self._school_context = """
🏫 CONTEXTO DE LA ESCUELA:
- Escuela primaria "PROF. MAXIMO GAMIZ FERNANDEZ"
- Ciclo escolar 2024-2025
- 211 estudiantes registrados en grados 1° a 6°
- Sistema integral de gestión académica y administrativa
- Base de datos completa con información académica y personal

📊 DATOS DISPONIBLES:
- Información personal: nombres, CURPs, matrículas, fechas de nacimiento
- Datos académicos: grados, grupos, turnos, calificaciones
- Historial de constancias generadas
- Estadísticas y reportes académicos

🎯 USUARIOS DEL SISTEMA:
- Personal administrativo de la escuela
- Secretarios académicos
- Directivos que necesitan información precisa y rápida
"""
        return self._school_context

    @property
    def communication_patterns(self) -> str:
        """
        PATRONES DE COMUNICACIÓN unificados

        Define cómo el sistema debe responder en diferentes situaciones
        """
        if self._communication_patterns is None:
            self._communication_patterns = """
📋 PATRONES DE RESPUESTA:

🔍 PARA BÚSQUEDAS:
- Confirmo qué encontré antes de mostrar resultados
- Sugiero acciones de seguimiento relevantes
- Mantengo el contexto para referencias futuras

📄 PARA CONSTANCIAS:
- Explico el proceso paso a paso
- Confirmo datos antes de generar
- Menciono la vista previa automática
- Ofrezco opciones de seguimiento

❓ PARA AYUDA:
- Proporciono información clara y práctica
- Incluyo ejemplos reales del sistema
- Explico limitaciones cuando aplique
- Sugiero alternativas cuando sea útil

💬 PARA CONVERSACIÓN:
- Mantengo el contexto de la sesión completa
- Hago referencias a interacciones anteriores
- Sugiero acciones basadas en el historial
- Soy proactivo pero no invasivo

⚠️ PARA ERRORES:
- Explico qué salió mal en términos simples
- Sugiero soluciones alternativas
- Mantengo un tono positivo y útil
- Ofrezco ayuda adicional si es necesario
"""
        return self._communication_patterns

    def get_unified_prompt_header(self, specific_role: str = "") -> str:
        """
        ENCABEZADO UNIFICADO para todos los prompts

        Args:
            specific_role: Rol específico del módulo (ej: "detector de intenciones", "generador de ayuda")

        Returns:
            Encabezado completo con identidad unificada
        """
        role_section = f"\n🎯 ROL ESPECÍFICO: {specific_role}\n" if specific_role else ""

        return f"""
{self.unified_identity}

{self.school_context}

{role_section}

{self.communication_patterns}

---
"""

    def get_conversation_context_template(self, conversation_stack: list = None) -> str:
        """
        TEMPLATE unificado para contexto conversacional

        Garantiza que todos los módulos manejen el contexto de la misma manera
        """
        if not conversation_stack:
            return "\n💭 CONTEXTO CONVERSACIONAL: Esta es una nueva conversación.\n"

        context = "\n💭 CONTEXTO CONVERSACIONAL:\n"
        context += "Historial de nuestra conversación actual:\n"

        for i, entry in enumerate(conversation_stack[-3:], 1):  # Últimas 3 interacciones
            role = "Usuario" if entry.get('role') == 'user' else "Yo"
            message = entry.get('content', '')[:100] + "..." if len(entry.get('content', '')) > 100 else entry.get('content', '')
            context += f"{i}. {role}: {message}\n"

        context += "\nDebo mantener continuidad con esta conversación.\n"
        return context

    def get_unified_json_instructions(self, json_structure: Dict[str, Any]) -> str:
        """
        INSTRUCCIONES JSON unificadas

        Garantiza formato consistente en todas las respuestas JSON
        """
        import json
        # Convertir la estructura a JSON válido como ejemplo
        json_example = json.dumps(json_structure, indent=2, ensure_ascii=False)

        return f"""
📋 FORMATO DE RESPUESTA OBLIGATORIO:
Responde ÚNICAMENTE con un JSON válido siguiendo esta estructura EXACTA:

{json_example}

⚠️ REGLAS CRÍTICAS PARA JSON:
- USA COMILLAS DOBLES (") para todas las cadenas, NO comillas simples (')
- NO agregues explicaciones fuera del JSON
- NO uses formato de diccionario de Python
- El JSON debe ser parseable con json.loads()
- Mantén exactamente los nombres de campos mostrados
- Usa "true"/"false" para booleanos, no True/False

✅ CORRECTO: {{"intention_type": "ayuda_sistema"}}
❌ INCORRECTO: {{'intention_type': 'ayuda_sistema'}}
"""
