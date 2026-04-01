import os
import sqlite3
import shutil
from urllib.parse import urlparse
from models import HistoryItem

class BrowserHistory:
    def get_history(self, limit=20):
        history_items = []
        try:
            appdata = os.getenv('LOCALAPPDATA')
            edge_path = os.path.join(appdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'History')
            chrome_path = os.path.join(appdata, 'Google', 'Chrome', 'User Data', 'Default', 'History')
            
            target_path = edge_path
            if os.path.exists(chrome_path):
                target_path = chrome_path
                
            temp_path = "temp_history_db"
            shutil.copy2(target_path, temp_path)
            
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            for row in rows:
                url = row[0]
                title = row[1] if row[1] else url
                domain = urlparse(url).netloc
                history_items.append(
                    HistoryItem(
                        title=title, 
                        url=url, 
                        domain=domain, 
                        visit_time=str(row[2]), 
                        favicon_path=""
                    )
                )
                
            conn.close()
            os.remove(temp_path)
        except:
            pass
        return history_items