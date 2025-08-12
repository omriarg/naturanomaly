import os
import pandas as pd
from django.conf import settings
from .SysPrompts_LLM import SYS_PROMPTS
from .cleanData import preprocess_data_without_embedding
import pandasql as psql
from vanna.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
class VannaVideoWrapper:
    #this is a wrapper class for Vanna
    #and Context Management for the current video behing discussed
    #Vanna is a library to improve performance of text-to-sql with LLM's
    #the current instance contains all the information about the Video
    #including paths,detections DF's,

    class _MyVanna(ChromaDB_VectorStore, Ollama):
        def __init__(self, config=None):
            ChromaDB_VectorStore.__init__(self, config=config)
            Ollama.__init__(self, config=config)

    def __init__(self, video_id: int, model: str = "llama3.2:3b"):
        self.video_id = video_id
        self.model = model
        self.base_dir = settings.BASE_DIR
        self.vector_store_dir = os.path.join(self.base_dir, "vector_store")#for vn
        self.training_data = SYS_PROMPTS.get("training_data", [])
        self.video_dir=os.path.join(self.base_dir, "DataProccessor", "processed_video")
        # Initialize Vanna (vector store + model)
        self.vn = self._MyVanna(config={"model": self.model, "path": self.vector_store_dir})

        # Load CSV for current video
        self._load_video_df(self.video_id)

        # Bind SQL runner
        self._bind_sql_runner()

        # Initial one-time training
        self._ensure_training()
    def get_video_dir(self):
        return self.video_dir
    def _load_video_df(self, video_id: int):
        csv_path = os.path.join(self.video_dir, f"Video{video_id}", "tracked_objects.csv")
        self.df = pd.read_csv(csv_path)

    def _bind_sql_runner(self):
        def run_sql(sql: str) -> pd.DataFrame:
            try:
                return preprocess_data_without_embedding(psql.sqldf(sql, {"df": self.df}))
            except Exception:
                return pd.DataFrame()

        self.vn.run_sql = run_sql
        self.vn.run_sql_is_set = True

    def get_video_id(self):
        return self.video_id
    def _ensure_training(self):
        existing = self.vn.get_training_data()
        has_ddl = (not existing.empty) and any(existing["training_data_type"] == "ddl")

        if not has_ddl:
            self.vn.train(
                ddl=("CREATE TABLE df (bbox TEXT, track_id INTEGER, object_name TEXT, time_date TEXT, "
                     "bbox_image_path TEXT, confidence REAL, score REAL)")
            )

        if self.training_data:
            asked = [] if existing.empty else list(existing["question"])
            for q, s in self.training_data:
                if q not in asked:
                    self.vn.train(question=q, sql=s)


    def set_video_context(self, new_video_id: int):
        """
        Switch to a different video without retraining or reinitializing the vector store.
        """
        if new_video_id == self.video_id:
            return  # No change

        self.video_id = new_video_id
        self._load_video_df(self.video_id)
        self._bind_sql_runner()


    def run_sql(self, sql: str) -> pd.DataFrame:
        return self.vn.run_sql(sql)

    def execute_sql(self, query: str, summarize_threshold: int = 10):
        """
        NL -> SQL via Vanna, run, and (optionally) summarize small results.
        """
        try:
            sql =  self.vn.generate_sql(query, allow_llm_to_see_data=True)
            result_df = self.run_sql(sql)
            from .queryOllama import respond_to_user

            if result_df is None or result_df.empty:
                return "No rows returned for this query."

            if len(result_df) <= summarize_threshold:
                context_block = (
                    f"The user asked: **{query}**\n\n"
                    f"The system generated SQL:\n```sql\n{sql}\n```\n"
                    f"Result:\n{result_df.to_string(index=False)}\n"
                )
                return respond_to_user(SYS_PROMPTS["execute_sql"] + "\n" + context_block)

            return result_df

        except Exception as e:
            return f"Error in execute_sql: {e}"