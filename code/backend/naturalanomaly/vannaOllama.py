import pandas as pd
import pandasql as psql
from vanna.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
import plotly.express as plx
# Define a custom Vanna class combining Ollama and ChromaDB
class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

# Initialize Vanna with model and ChromaDB vector store
vn = MyVanna(config={
    'model': 'llama3.2:3b',
    'persist_directory': './vector_store'
})

# Load CSV as DataFrame
df = pd.read_csv("tracked_objects.csv")

# Define SQL runner on DataFrame using pandasql
def run_sql(sql):
    try:
        return psql.sqldf(sql, {'df': df})
    except Exception as e:
        print(f"SQL execution error: {e}")
        return pd.DataFrame()

# Register run_sql with Vanna
vn.run_sql = run_sql
vn.run_sql_is_set = True
print("DataFrame connected and SQL runner set.")

# Train Vanna with questions and SQL queries
training_data = [
    ("Which track_id had the lowest confidence score?",
     "SELECT track_id, MIN(confidence) AS lowest_confidence FROM df GROUP BY track_id ORDER BY lowest_confidence ASC LIMIT 1;"),

    ("What are the top 5 object types by average confidence?",
     "SELECT object_name, AVG(confidence) AS avg_confidence FROM df GROUP BY object_name ORDER BY avg_confidence DESC LIMIT 5;"),

    ("What is the average score for each track_id?",
     "SELECT track_id, AVG(score) AS avg_score FROM df GROUP BY track_id ORDER BY avg_score DESC;"),

    ("How many unique object types were detected?",
     "SELECT COUNT(DISTINCT object_name) AS unique_object_types FROM df;"),

    ("Which track_id had the most recent detection?",
     "SELECT track_id, MAX(time_date) AS last_seen FROM df GROUP BY track_id ORDER BY last_seen DESC LIMIT 1;"),

    ("What is the average confidence score across the dataset?",
     "SELECT AVG(confidence) AS overall_avg_confidence FROM df;")
]

for question, sql in training_data:
    vn.train(question=question, sql=sql)

# Ask a question after training
sql=vn.generate_sql("show all trucks and time their time of detection")
answer_df=run_sql(sql)
print(answer_df)
sql=vn.generate_sql("what is the busiest time?")
answer_df=run_sql(sql)
print(answer_df)
