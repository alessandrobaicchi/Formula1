import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model


    def handleCreaGrafo(self,e):
        pass
    def handleDettagli(self, e):
        pass
    def handleCerca(self, e):
        pass


    # ------------------------------------ ddAnno1 ddAnno2 --------------------------------------------
    def fillDDYears(self):
        # years contiene interi --> li metto direttamente come valori dei dd
        years = self._model.getAllYears()
        for y in years:
            self._view._ddAnno1.options.append(ft.dropdown.Option(y))
            self._view._ddAnno2.options.append(ft.dropdown.Option(y))
        self._view.update_page()
    # -------------------------------------------------------------------------------------------------