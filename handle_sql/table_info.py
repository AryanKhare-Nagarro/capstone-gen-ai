from langchain_community.utilities import SQLDatabase
from state import DataState
import ast

def get_table_info(filepath: str, state: DataState):

    # extract the file name with extention and use it like "sqlite:///filename.db"
    DB = SQLDatabase.from_uri(filepath)
    tables = DB.get_usable_table_names()

    full_schema_text = {}
    for table in tables:
        schema_text = f"Table: {table}\nColumns: "
        columns = DB.run(f"PRAGMA table_info({table})")
        foreign_keys = DB.run(f"PRAGMA foreign_key_list({table})")
        columns = ast.literal_eval(str(columns))
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            pk = "Primary Key" if col[5] == 1 or col[5] == 2 else ""
            schema_text += f"\n- {col_name}: {col_type}" + (f", {pk}" if pk else "")
        
        if foreign_keys:
            schema_text += "\nForeign Keys:"
            foreign_keys = ast.literal_eval(str(foreign_keys))
            
            for fk in foreign_keys:
                schema_text += f"\n- {table}.{fk[3]} -> {fk[2]}.{fk[4]}"
        
        full_schema_text[table] = schema_text
    return full_schema_text