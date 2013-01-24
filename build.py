# -*- coding: utf-8 -*-
import folio
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

template_path = os.path.abspath('templates')

if __name__ == '__main__':
    folio.build(template_path=template_path)
    
    def handler(self, event):
        if not event.is_directory:
            print '%s %s' % (event.src_path, event.event_type)
            folio.build(template_path=template_path)
    
    EventHandler = type('EventHandler', (FileSystemEventHandler, ),
                        {'on_any_event': handler})
    observer = Observer()
    observer.schedule(EventHandler(), path=template_path, recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()