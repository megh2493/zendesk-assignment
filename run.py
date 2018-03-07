import requests
import webbrowser

from multiprocessing import Process

from app import app


# waits till server is ready, then opens the login page
def open_browser(url):
    while True:
        try:
            requests.get(url, timeout=0.5)
            webbrowser.open(url)
            return
        except requests.exceptions.ConnectionError:
            pass


if __name__ == '__main__':
    host = app.config.get('HOST', '127.0.0.1')
    port = app.config.get('PORT', 5000)
    Process(target=open_browser, args=('http://%s:%s/' % (host, port),)).start()
    app.run(host=host, port=port) # start the application
