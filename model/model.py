import networkx as nx
from networkx.classes import subgraph

from database.DAO import DAO

class Model:
    def __init__(self):
        self._graph = nx.Graph()
        self._idMapDrivers = {}
        self._drivers = []

    # -------------------------------------- Crea grafo + info ----------------------------------------------
    def buildGraph(self, year1, year2):
        self._graph.clear()

        self._drivers = DAO.getAllNodes(year1, year2)

        # Mi creo il "solito" idMap, tanto mi servirà dopo...
        for d in self._drivers:
            self._idMapDrivers[d.driverId] = d

        # Aggiungo i nodi alla grafo
        self._graph.add_nodes_from(self._drivers)

        # Aggiungo gli archi al grafo
        edges = DAO.getAllEdges(year1, year2, self._idMapDrivers)
        for e in edges:
            self._graph.add_edge(e.d1, e.d2, weight = e.peso)


    def getGraphDetails(self):
        return len(self._graph.nodes), len(self._graph.edges)

    # ------------------------------------------------------------------------------------------------

    # ------------------------------- I 3 archi di peso maggiore -------------------------------------
    # Ottengo tutti gli archi del grafo.
    # edges(data=True) restituisce tuple del tipo:
    # (nodo1, nodo2, {"weight": valore})
    # quindi x[2] è il dizionario degli attributi dell’arco
    # e x[2]["weight"] è il peso dell’arco.

    # Ordino tutti gli archi in base al peso (decrescente)
    # usando come chiave il peso contenuto nel dizionario degli attributi.
    # sorted(...) produce una lista ordinata di archi.

    # [:3] prende solo i primi 3 archi più pesanti.
    def getTop3Archi(self):
        return sorted(self._graph.edges(data=True), key = lambda x : x[2]["weight"], reverse=True)[:3]
    # -------------------------------------------------------------------------------------------------

    # ------------------------------- Componenti connesse + info --------------------------------------
    def getConnessaInfo(self):
        # ------------------------------------------------------------
        # COMPONENTI CONNESSE + INFO (Punto 3b e 3c dell’esame)
        #
        # 1) Ottengo tutte le componenti connesse del grafo:
        #    nx.connected_components(G) restituisce un generatore di insiemi,
        #    dove ogni insieme rappresenta una componente connessa.
        #
        #    Esempio:
        #    components = [
        #        {hamilton, alonso, massa, kovalainen},   # comp. grande
        #        {kubica, heidfeld},
        #        {rosberg},
        #        ...
        #    ]
        #
        # ------------------------------------------------------------
        components = list(nx.connected_components(self._graph))
        # E' una lista di componenti connesse

        # ------------------------------------------------------------
        # 2) Trovo la componente connessa più grande:
        #    max(..., key=len) sceglie l’insieme con più nodi.
        #
        #    Esempio:
        #    largest = {hamilton, alonso, massa, kovalainen}
        #
        # ------------------------------------------------------------
        largest = max(components, key = len)

        # ------------------------------------------------------------
        # 3) Creo un sottografo contenente SOLO i nodi della componente
        #    più grande. Questo permette di calcolare il grado dei nodi
        #    considerando solo gli archi interni alla componente.
        #
        #    Esempio di sottografo:
        #       hamilton -- alonso
        #       hamilton -- massa
        #       alonso   -- massa
        #       massa    -- kovalainen
        #
        # ------------------------------------------------------------
        subgraph = self._graph.subgraph(largest).copy()

        # ------------------------------------------------------------
        # 4) Ordino i nodi della componente più grande in base al grado
        #    (numero di archi incidenti), in ordine decrescente.
        #
        #    Esempio:
        #    Gradi nel sottografo:
        #       massa       → 3
        #       hamilton    → 2
        #       alonso      → 2
        #       kovalainen  → 1
        #
        #    Risultato:
        #    orderedNodes = [massa, hamilton, alonso, kovalainen]
        #
        # ------------------------------------------------------------
        orderedNodes = sorted(subgraph.nodes(), key = lambda n : self._graph.degree(n), reverse = True)

        # ------------------------------------------------------------
        # 5) Creo la lista finale dei dettagli: (nodo, grado)
        #
        #    Esempio:
        #    details = [
        #        (massa, 3),
        #        (hamilton, 2),
        #        (alonso, 2),
        #        (kovalainen, 1)
        #    ]
        #
        #    Questa lista è quella che il Controller stamperà.
        #
        # ------------------------------------------------------------
        details = [(n, self._graph.order(n)) for n in orderedNodes]

        # ------------------------------------------------------------
        # 6) Ritorno:
        #    - numero totale di componenti connesse
        #    - la componente più grande (insieme di nodi)
        #    - i nodi della componente più grande ordinati per grado
        # ------------------------------------------------------------
        return len(components), largest, details
    # -------------------------------------------------------------------------------------------------

    # ------------------------------------ ddAnno1 ddAnno2 --------------------------------------------
    def getAllYears(self):
        return DAO.getAllYears()
    # -------------------------------------------------------------------------------------------------