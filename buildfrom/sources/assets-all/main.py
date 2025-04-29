import multiprocessing
multiprocessing.set_start_method("spawn",force=True)
if __name__ == '__main__':
    import gui.home
    gui.home.startApp()