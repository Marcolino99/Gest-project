# Gest-project
 Gaming Search Engine
 
### Dependencies

Il programma per funzionare ha bisogno di:
    - nella fase di indexing beautifulsoup4, gevent, whoosh
    - nella fase di searching whoosh
    - per la GUI wxpython

### Dump Collection

Per scaricare un test della collection, eseguire il file "quickdump.py". Scaricherà un numero desiderato
di documenti per ogni piattaforma.

**ATTENZIONE**: Nonostante sia possibile scaricare file sia dal sito www.ign.com sia utilizzando le API di igdb, da quickdump.py
quest\'ultima opzione non è disponibile perchè sarebbe necessario rinnovare il token di accesso alle api tramite un SecretId di twitch personale
di un membro del gruppo, anche se è implementata nel progetto e funzionante.

### Program Launch

Per avviare il programma eseguire "wxglade_out.py". Cercherà un indice valido nella directory corrente + */collection/indexdir*. Nel caso in cui non lo
trovi chiederà se si desidera crearlo.