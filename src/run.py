from app.app import App

def run() -> None:
    app = App()
    app.run()
    del app

if __name__ == '__main__':
    run()
