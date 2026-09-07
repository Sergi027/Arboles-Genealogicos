from dataclasses import dataclass, field
from typing import Optional
from datetime import date  # Para representar fechas mediante 
from enum import Enum



class Sexo(Enum):  # Para representar sexos
    MASCULINO = "M"
    FEMENINO = "F"
    DESCONOCIDO = "?"  # TODO: Implementar esta posibilidad en todas las funciones
    


@dataclass
class Persona:

    #------------------- ATRIBUTOS -------------------#
    nombre: str
    apellido1: Optional[str]
    apellido2: Optional[str]
    sexo: Sexo

    # Opcionales
    fecha_nacimiento: Optional[date] = None
    fecha_muerte: Optional[date] = None
    lugar_nacimiento: Optional[str] = None
    alias: Optional[str] = None

    # Progenitores
    progenitores: Optional[Pareja] = None
    @property
    def padre(self) -> Optional["Persona"]:
        return self.progenitores.hombre if self.progenitores else None
    @property
    def madre(self) -> Optional["Persona"]:
        return self.progenitores.mujer if self.progenitores else None

    # Cónyuges
    parejas: list[Pareja] = field(default_factory=list)
    @property
    def conyuges(self) -> list["Persona"]:
        return [p.mujer if self is p.hombre else p.hombre for p in self.parejas]

    # Hijos
    @property
    def hijos(self) -> list["Persona"]:
        return [h for p in self.parejas for h in p.hijos]
    
    #------------- REPRESENTACIÓN Y HASH -------------#
    @property
    def nombre_completo(self) -> str:  # P.ej. Pablo Pérez López
        return f"{self.nombre} {self.apellido1} {self.apellido2}".strip()
 
    def __repr__(self) -> str:
        return self.nombre_completo

    @property
    def clave(self) -> str:  # P.ej. Pablo Pérez López (tío Pablo)
        if self.alias:
            return f"{self.nombre_completo} ({self.alias})"
        return self.nombre_completo

    def __hash__(self):
        return hash(self.clave)



@dataclass
class Pareja:

    #------------------- ATRIBUTOS -------------------#
    hombre: Persona
    mujer: Persona
    hijos: list[Persona] = field(default_factory=list)

    #------------- COMPROBACIÓN DE SEXOS -------------#
    def __post_init__(self):
        if self.hombre.sexo != Sexo.MASCULINO:
            raise ValueError(f"{self.hombre.nombre_completo} debe tener sexo HOMBRE")
        if self.mujer.sexo != Sexo.FEMENINO:
            raise ValueError(f"{self.mujer.nombre_completo} debe tener sexo MUJER")
        ##self.hombre.pareja_propia = self
        ##self.mujer.pareja_propia = self

    #------------- REPRESENTACIÓN Y HASH -------------#
    def __repr__(self) -> str:
        return f"{self.hombre.nombre_completo} & {self.mujer.nombre_completo}"
 
    def __hash__(self):
        return hash(self.hombre.nombre_completo, self.mujer.nombre_completo)

    #--------------------- HIJOS ---------------------#
    def agregar_hijo(self, hijo: Persona) -> Persona:
        hijo.progenitores = self
        self.hijos.append(hijo)
        return hijo



class ArbolGenealogico:

    #------------------- ATRIBUTOS -------------------#
    def __init__(self, nombre_arbol: str):
        self.nombre_arbol = nombre_arbol
        self.personas: dict[str, Persona] = {}  # La colección de personas es un diccionario indexado por clave
        self.parejas: dict[tuple[str, str], Pareja] = {}  # La colección de parejas es un diccionario indexado por (clave, clave)
        self._indice_alias: dict[str, list[Persona]] = {}  # Un índice de todos los alias para buscar más rápido

    #--------- GESTIÓN DE PERSONAS Y PAREJAS ---------#
    def agregar_persona(self, persona: Persona) -> Persona:
        if persona.clave in self.personas:
            raise ValueError(
                f"Ya existe una persona con la clave '{persona.clave}'. "
                f"Usa el campo 'alias' para diferenciarlas "
            )
        self.personas[persona.clave] = persona
        if persona.alias:
            self._indice_alias.setdefault(persona.alias, []).append(persona)
        return persona
 
    def formar_pareja(self, hombre: Persona, mujer: Persona) -> Pareja:
        pareja = Pareja(hombre, mujer)
        self.parejas[(hombre.clave,mujer.clave)] = pareja
        return pareja
 
    def agregar_hijo(self, pareja: Pareja, hijo: Persona) -> Persona:
        self.agregar_persona(hijo)
        return pareja.agregar_hijo(hijo)

    #------------------- BÚSQUEDA --------------------#
    def buscar(self, clave: str) -> Optional[Persona]:  # Busca por clave: 'Nombre Apellido1 Apellido2 (alias)'
        return self.personas.get(clave)
 
    def buscar_por_nombre(self, nombre_completo: str) -> list[Persona]:  # Busca todas las personas con un mismo nombre completo
        return [p for p in self.personas.values() if p.nombre_completo == nombre_completo]

    def buscar_por_alias(self, alias: str) -> Persona:  # Devuelve la única persona con ese alias. Si no existe ninguna, lanza KeyError; si hay varias, lanza ValueError con las claves de todas ellas
        coincidencias = self._indice_alias.get(alias, [])
        if not coincidencias:
            raise KeyError(f"No existe ninguna persona con alias '{alias}'.")
        if len(coincidencias) > 1:
            claves = [p.clave for p in coincidencias]
            raise ValueError(
                f"Hay {len(claves)} personas con alias '{alias}', usa buscar() "
                f"con la clave completa para desambiguar: {claves}"
            )
        return coincidencias[0]

    def buscar_pareja(self, hombre: Persona, mujer: Persona) -> Optional[Pareja]:  # Busca una pareja con (clave_hombre,clave_mujer)
        return self.parejas.get((hombre.clave, mujer.clave))
 
    def buscar_pareja_de(self, clave_persona: str) -> Optional[Pareja]:  # Busca las parejas de una persona
        persona = self.buscar(clave_persona)
        return persona.parejas if persona else []

    #------------------- CONSULTAS -------------------#
    def ascendientes(self, persona: Persona) -> list[Persona]:
        pass

    def descendientes(self, persona: Persona) -> list[Persona]:
        pass

    def apellidos_todos(self, persona: Persona) -> list[str]:
        pass

    def parentesco(self, persona1: Persona, persona2: Persona):
        pass

    #----------- BÚSQUEDA DE INCONSISTENCIAS -----------#
    def depurar_apellidos(self):  # Miramos si los apellidos son inconsistentes con padres o hijos:
        for persona in self.personas.values():
            valid = False  # Apellido 1
            if (persona.apellido1 == persona.padre.apellido1):  # Se mira el padre
                if persona.sexo == Sexo.MASCULINO:  # Se miran los hijos si persona es hombre
                    for hijo in persona.hijos:
                        if hijo.apellido1 == persona.apellido1:
                            valid = True
                elif persona.sexo == Sexo.FEMENINO:  # Se miran los hijos si persona es mujer
                    for hijo in persona.hijos:
                        if hijo.apellido2 == persona.apellido1:
                            valid = True
            if not valid:
                raise ValueError("Apellido1 inconsistente")
            valid = False  # Apellido 2
            if (persona.apellido2 == persona.madre.apellido1):  # Se mira la madre
                valid = True  # Los hijos no dan información sobre el segundo apellido
            if not valid:
                raise ValueError("Apellido2 inconsistente")
            
    #------------ COMPLETADO DE INFORMACIÓN ------------#
    def completar_apellidos(self):
        for persona in self.personas.values():  # TODO: ir de abajo a arriba
            
            # Si los apellidos no están determinados:
            if persona.apellido1 == None:
                persona.apellido1 = persona.padre.apellido1  # Se mira primero a los padres
            if persona.apellido1 == None:
                if persona.sexo == Sexo.MASCULINO:
                    persona.apellido1
                    pass
    

    #------------- OPERACIONES CON ÁRBOLES -------------#
    def integrar_arbol(self, arbol2: ArbolGenealogico):
            pass
    
    def subarbol_descendientes_de(self, p: Persona|Pareja) -> ArbolGenealogico:
        subarbol = ArbolGenealogico(f"Descendientes de {p}")
        if type(p) == Persona:
            for pareja in p.parejas:
                subarbol.integrar_arbol(self.subarbol_descendientes_de(pareja))

    




#--------------- TODOLIST: ---------------#
# TODO: Función que complete apellidos hacia abajo. Será especialmente útil aplicada sobre el subárbol de descendientes de alguien. 
# (Para que los cambios en el subárbol se apliquen al árbol principal, necesitaremos una función que actualice árboles).
# TODO: Función que complete los apellidos hacia arriba.
# TODO: Representación gráfica de árboles.
# TODO: Función que exporte un árbol a un JSON.
# TODO: Función que saque los cumpleaños y los ordene por su posición en el año.
