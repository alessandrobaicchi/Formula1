import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    # ---------------------------------------- Pulsante "Crea grafo" -----------------------------------------------
    def handleCreaGrafo(self,e):
        self._model.buildGraph(self._view._ddAnno1.value, self._view._ddAnno2.value)
        Nnodes, Nedges = self._model.getGraphDetails()
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"Grafo creato correttamente. Il grafo contiene {Nnodes} nodi"
                                                      f" e {Nedges} archi."))
        self._view.update_page()
    # --------------------------------------------------------------------------------------------------------------

    # --------------------------------------- Pulsante "Stampa dettagli" -------------------------------------------
    def handleDettagli(self, e):
        top3 = self._model.getTop3Archi()
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Archi di peso maggiore:"))
        for arco in top3:
            self._view.txt_result.controls.append(ft.Text(f"{arco[0]} -> {arco[1]} (peso: {arco[2]["weight"]})"))

        numero, largest, details = self._model.getConnessaInfo()
        self._view.txt_result.controls.append(ft.Text(f"Il grafo contiene {numero} componenti connesse."))
        self._view.txt_result.controls.append(ft.Text(f"La componente connessa maggiore ha dimensine pari a: "
                                                      f"{len(largest)}."))
        for l in largest:
            self._view.txt_result.controls.append(ft.Text(l))

        self._view.txt_result.controls.append(ft.Text("Componente connessa in ordine decrescente di grado di nodi."))
        for d in details:
            self._view.txt_result.controls.append(ft.Text(f"{d[0]} - grado: {d[1]}"))

        self._view.update_page()
    # --------------------------------------------------------------------------------------------------------------

    # ---------------------------------------- Pulsante "Cerca lista piloti" ---------------------------------------
    def handleCerca(self, e):
        k = self._view._txtInK.value
        # Qui dovrei fare i soliti controlli sulla validità di k...

        kInt = int(k)

        listPilotiOttima, minDistEta = self._model.getListaPilotiOttima(kInt)

        if listPilotiOttima is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text(f"Non ci sono abbastanza componenti connesse per trovare {kInt}"
                                                          f" piloti che non siano stati compagni di squadra nel range"
                                                          f" selezionato."))
            return

        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Lista di piloti con scarto di età minimo che non sono stati "
                                                      "mai compagni di squadra nel range selezionato."))
        for p in listPilotiOttima:
            self._view.txt_result.controls.append(ft.Text(p))
        self._view.txt_result.controls.append(ft.Text(f"La differenza di età fra il pilota più giovave e il pilota "
                                                      f"più vecchio è pari a {minDistEta} giorni."))
        youngest = min(listPilotiOttima, key=lambda x : x.dob)
        oldest = max(listPilotiOttima, key=lambda x: x.dob)
        self._view.txt_result.controls.append(ft.Text(f"Pilota più anziano: {oldest}"))
        self._view.txt_result.controls.append(ft.Text(f"Pilota più giovane: {youngest}"))

        self._view.update_page()
    # --------------------------------------------------------------------------------------------------------------

    # ------------------------------------ ddAnno1 ddAnno2 --------------------------------------------
    def fillDDYears(self):
        # years contiene interi --> li metto direttamente come valori dei dd
        years = self._model.getAllYears()
        for y in years:
            self._view._ddAnno1.options.append(ft.dropdown.Option(y))
            self._view._ddAnno2.options.append(ft.dropdown.Option(y))
        self._view.update_page()
    # -------------------------------------------------------------------------------------------------