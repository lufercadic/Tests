# coding: utf8
import sys
sys.path.append("")
import pandas as panda


# Clase que extiende la libreria pandas y da acceso a los datos exportados desde el sistema RedCap
@panda.api.extensions.register_dataframe_accessor("Redcap")
class RedcapPlugin():
    """Clase que extiende la libreria pandas y da acceso a los datos exportados desde el sistema RedCap"""
    #Constructor de objeto
    def __init__(self, panda_obj):
        """Constructor"""
        self.__obj = panda_obj # obtenemos una refencia del objeto pandas
        self.__projects = self.__getProjects() # obtenemos los metadatos        

    # Obtiene los meta-datos de los proyectos presentes en el archivo
    def __getProjects(self):
        """Obtiene los meta-datos de los proyectos presentes en el archivo"""
        pl = {}
        ini = 0
        fin = 0
        name = None
        for v in self.__obj.columns.values:
            if v.endswith('_complete'):
                name = v[:-9]
                pl[name] = { 'name': name, 'findex': ini, 'lindex': fin }
                #print(pl[name], self.__obj.columns.values[ini:fin+1])
                ini = fin + 1
            fin = fin + 1
        return pl

    # Retorna una lista con los nombres de los proyectos en el archivo importado
    @property
    def projects_list(self):
        """Retorna una lista con los nombres de los proyectos en el archivo importado"""
        return [*self.__projects.keys()]

    # Retorna la lista de columnas asociadas a un proyecto especifico
    def project_columns(self, name):
        """Retorna la lista de columnas asociadas a un proyecto especifico"""
        try:
            p = self.__projects[name]
            list = self.__obj.columns.values[p['findex']:p['lindex']+1]
            return None
        except KeyError as err:
            #print(err)
            return None

    # Retorna los metadatos de un proyecto especifico
    def project_metadata(self, name):
        """Retorna los metadatos de un pryecto especifico"""
        try:
            p = self.__projects[name]
            return dict(p)
        except KeyError:
            return None

    # Retorna los metadatos de un pryecto especifico
    def project_dataframe(self, name):
        """Retorna los metadatos de un pryecto especifico"""
        try:
            p = self.__projects[name]
            #return self.__obj.iloc[:, p['findex']:p['lindex']+1] # Dataframe con los datos de un proyecto especifico
            return self.__obj.iloc[:, p['findex']:p['lindex']+1].dropna(thresh=2) # Dataframe con los datos de un proyecto especifico, filtra las filas que estan totalmente vacias.
        except KeyError:
            return None

    # Importa un archivo RedCap csv y crea un objeto pandas
    @classmethod
    def load_file(cls, filepath):
        """Importa un archivo RedCap csv y crea un objeto pandas"""
        return panda.read_csv(filepath)








# Procedimiento main, se usa solo para depuracion
def Main(args):
    file = "demofile.csv" # Archivo de ejemplo
    if(len(args) > 1): file = args[1] # si hay un segundo parametro, se usa como el archivo a abrir
    print("File:", file)
    pd = RedcapPlugin.load_file(file) # se crea el archivo pandas
    tmp = pd.Redcap.project_dataframe('screening') # se obtiene los datos de un solo formulario
    print(tmp) # se imprime en pantalla


# Permite depurar si se llama directamente
if __name__ == '__main__':
	Main(sys.argv)