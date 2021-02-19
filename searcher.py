from whoosh.index import open_dir
from whoosh import qparser
from whoosh import scoring

class Searcher:

    def __init__(self,path,weight=None):
        self.ix = open_dir(path)
        
        weights = {"pos_scor": scoring.FunctionWeighting(pos_score_fn),
                   "tf_idf": scoring.TF_IDF(),
                   "BM25": scoring.BM25F(B=0.75, content_B=1.0, K1=1.5)}
        
        
        
        if not weight == None:
            self.searcher = self.ix.searcher(weighting = weights[weight])
        else:
            self.searcher = self.ix.searcher()

    def group(self, mode):
        switch = {
            'factory_or': qparser.OrGroup.factory(0.9),
            'and': qparser.AndGroup,
            'or': qparser.OrGroup
        }
        
        self.group = switch.get(mode, qparser.OrGroup.factory(0.9))

    def parse(self, proc_query,field="content"):
        parser = qparser.QueryParser(field, schema=self.ix.schema, group=self.group)        
        self.query = parser.parse(str(proc_query))
        print(self.query)

    def search(self,limit=10):
        results = self.searcher.search(self.query,limit=limit,terms = True)
        return results


#position based scoring function
def pos_score_fn(searcher, fieldname, text, matcher):
    poses = matcher.value_as("positions")
    return 1.0 / (poses[0] + 1)




