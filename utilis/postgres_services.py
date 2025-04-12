import json
import psycopg2


class PostgresServices:
    def __init__(self, postgres_config, postgres_database_config):
        self.postgres_config = postgres_config
        self.postgres_database_config = postgres_database_config

    def connect_postgres(self):
        postgres_config = self.postgres_config
        pg_host = postgres_config['host']
        pg_database = postgres_config['database']
        pg_user = postgres_config['user']
        pg_password = postgres_config['password']

        return psycopg2.connect(host=pg_host, database=pg_database, user=pg_user, password=pg_password)

    def read_data_from_postgres(self, query_table_name):
        conn = self.connect_postgres()
        cursor = conn.cursor()
        query = f"SELECT * FROM {query_table_name};"
        df = pd.read_sql(query, conn)

        # Close connection
        cursor.close()
        conn.close()

        return df

    def save_embedding_to_postgres(self, query_table_name, input, embedding):
        conn = self.connect_postgres()
        cursor = conn.cursor()

        cols = self.postgres_database_config[query_table_name]['cols']
        cols_str = ", ".join([f"{col} {dtype}" for col, dtype in cols.items()])
        col_names = list(cols.keys())[1:]  # Bỏ qua ID
        placeholders = ", ".join(["%s"] * len(col_names))

        # Giá trị của các cột (trừ ID)
        values = [input.get(col, None) for col in col_names[:-1]]
        values.append(embedding)

        # Check extension "pgvector" has created
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Check table if it not exists
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {query_table_name} (
                {cols_str}
            );
        """
        cursor.execute(create_table_query)
        conn.commit()

        # Chèn dữ liệu
        insert_query = f"""
            INSERT INTO {query_table_name} ({', '.join(col_names)})
            VALUES ({placeholders});
        """
        cursor.execute(insert_query, values)

        conn.commit()
        cursor.close()
        conn.close()



