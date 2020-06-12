from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from io import StringIO

class WebEngineView(QtWebEngineWidgets.QWebEngineView):
    """ Extends a QWebEngineView with functionality to show an Altair chart
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.page().profile().downloadRequested.connect(self.onDownloadRequested)
        self.windows = []

    @QtCore.pyqtSlot(QtWebEngineWidgets.QWebEngineDownloadItem)
    def onDownloadRequested(self, download):
        if (
            download.state()
            == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadRequested
        ):
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, self.tr("Save as"), download.path()
            )
            if path:
                download.setPath(path)
                download.accept()

    def createWindow(self, type_):
        if type_ == QtWebEngineWidgets.QWebEnginePage.WebBrowserTab:
            window = QtWidgets.QMainWindow(self)
            view = QtWebEngineWidgets.QWebEngineView(window)
            window.resize(640, 480)
            window.setCentralWidget(view)
            window.show()
            return view

    def updateChart(self, chart, **kwargs):
        output = StringIO()
        chart.save(output, "html", **kwargs)
        self.setHtml(output.getvalue())

    def loadCSS(self, css, name):
        SCRIPT = """
        (function() {
        css = document.createElement('style');
        css.type = 'text/css';
        css.id = "%s";
        document.head.appendChild(css);
        css.innerText = `%s`;
        })()
        """ % (name, css)
        script = QtWebEngineWidgets.QWebEngineScript()
        self.page().runJavaScript(SCRIPT, QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
        script.setName(name)
        script.setSourceCode(SCRIPT)
        script.setInjectionPoint(QtWebEngineWidgets.QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
        self.page().scripts().insert(script)
