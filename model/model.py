import copy

import networkx as nx
from networkx.classes import subgraph

from database.DAO import DAO

class Model:
    def __init__(self):
        self._graph = nx.Graph()
        self._idMapDrivers = {}
        self._drivers = []
        self._optListPiloti = None
        self._minDistGiorni = None

    # -------------------------------------- Crea grafo + info ----------------------------------------------
    # In questo metodo uso i MIEI DTO:
    # - Driver: come nodi del grafo
    # - Arco: solo per leggere d1, d2, peso dal DB
    #
    # Dopo che faccio add_edge(d1, d2, weight=peso),
    # NetworkX converte tutto nelle sue strutture interne.
    # Da qui in poi NON userò più il DTO Arco.

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

    # Qui NON uso il mio DTO Arco.
    # NetworkX restituisce gli archi come tuple:
    #   (nodo1, nodo2, {"weight": w})
    #
    # Quindi sorted(...) lavora su queste tuple,
    # non sugli oggetti Arco creati dal DAO.

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
        details = [(n, self._graph.degree(n)) for n in orderedNodes]

        # ------------------------------------------------------------
        # 6) Ritorno:
        #    - numero totale di componenti connesse
        #    - la componente più grande (insieme di nodi)
        #    - i nodi della componente più grande ordinati per grado
        # ------------------------------------------------------------
        return len(components), largest, details

    # Qui NON uso il DTO Arco.
    # Lavoro solo con:
    #   - set di nodi (che sono oggetti Driver)
    #   - sottografi NetworkX
    #   - gradi dei nodi calcolati da NetworkX
    #
    # I nodi sono i miei DTO Driver,
    # ma tutta la logica delle componenti e dei gradi
    # usa le strutture interne di NetworkX.

    # -------------------------------------------------------------------------------------------------


    # ------------------------------------ ddAnno1 ddAnno2 --------------------------------------------
    def getAllYears(self):
        return DAO.getAllYears()
    # -------------------------------------------------------------------------------------------------


    # ---------------------------------------- Ricorsione ---------------------------------------------
    # Qui uso SOLO i miei DTO Driver.
    # Le componenti connesse sono set di Driver.
    # La ricorsione costruisce liste di Driver.
    #
    # Nessuna tupla di NetworkX viene usata qui:
    # lavoro solo sui nodi (Driver), non sugli archi.

    def getListaPilotiOttima(self, k):
        self._optListPiloti = []
        self._minDistGiorni = 100*365 # Imposto un valore alto di default, perché devo trovare un minimo

        # Prendo tutte le componenti connesse del grafo
        components = list(nx.connected_components(self._graph))

        if len(components) < k:
            # Se entro qua vuol dire che non ci sono abbastanza componenti connesse da cui pescare i piloti,
            # e quindi non si può trovare una soluzione
            return None, 0

        parziale = []
        self._ricorsione(components, k, parziale, 0)

        return self._optListPiloti, self._minDistGiorni


    # Qui lavoro esclusivamente con i miei DTO Driver.
    # 'parziale' contiene Driver.
    # 'components[index]' è un set di Driver.
    #
    # NetworkX interviene solo per calcolare le componenti,
    # ma dentro la ricorsione manipolo SOLO i miei oggetti Driver.
    def _ricorsione(self, components, k, parziale, indexComponente):
        # Condizione di ottimalità
        if len(parziale) == k:
            # Allora ho una soluzione accettabile
            dateDiNascita = [p.dob for p in parziale]
            diffEtaPiloti = (max(dateDiNascita) - min(dateDiNascita)).days
            if diffEtaPiloti < self._minDistGiorni:
                self._optListPiloti = copy.deepcopy(parziale)
                self._minDistGiorni = diffEtaPiloti
            return

        # Condizione di terminazione
        # 1) Esco se l'indice che indica quale componente connessa sto considerando a questa iterezione,
        #    è diventato maggiore o uguale al numero di componenti connesse totali, perché vuol dire
        #    che non ho altre componenti connesse da cui pescare piloti.
        # 2) Altro motivo, è se non ho abbastanza componenti rimanenti per arrivare a k piloti in parziale.
        if indexComponente >= len(components) or (len(components) - indexComponente) < (k - len(parziale)):
            return


        # Se non sono uscito, allora posso aggiungere ancora piloti. Per questa componente, di indice indexComponente,
        # provo ad ingaggiare un pilota oppure a non ingaggiare nessuno.

        # Caso 1. Inserisco un pilota appartente a questa componente connessa. In questo branch provo tutti i piloti
        # che fanno parte della componente connessa.
        componente = components[indexComponente]
        for pilota in componente:
            parziale.append(pilota)
            self._ricorsione(components, k, parziale, indexComponente + 1)
            parziale.pop()

        # Caso 2. Mi tengo un branch di esplorazione in cui non ho preso nessuno da questa componente.
        self._ricorsione(components, k, parziale, indexComponente + 1)

    # -------------------------------------------------------------------------------------------------