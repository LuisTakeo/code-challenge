from pyspark.sql import SparkSession
import subprocess

def run_embulk(config_file):
    try:
        result = subprocess.run(['embulk', 'run', config_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode('utf-8'))
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running embulk with config {config_file}: {e.stderr.decode('utf-8')}")
        return False

def main():
    # Inicializa a sessão Spark
    spark = SparkSession.builder \
        .appName("Embulk Orchestrator") \
        .getOrCreate()
    sc = spark.sparkContext

    # Primeira transformação: Postgres para JSON
    first_task = sc.parallelize([1])\
        .map(lambda x: run_embulk("/config/postgres_to_json.yml"))\
            .collect()
    if all(first_task):
        print("First transformation succeeded.")
        second_task = sc.parallelize([1])\
            .map(lambda x: run_embulk("/config/csv_to_json.yml"))\
                .collect()
        if all(second_task):
            print("Second transformation succeeded.")
            # Combina os dados JSON usando Spark
            json_df1 = spark.read.json("/output/orders_postgres.json")
            json_df2 = spark.read.json("/output/orders_csv.json")
            combined_df = json_df1.union(json_df2)
            combined_df.write.json("/output/combined_orders.json")
            # Terceira transformação: JSON combinado para Postgres
            third_task = sc.parallelize([1])\
                .map(lambda x: run_embulk("/config/json_to_postgres.yml"))\
                    .collect()
            if all(third_task):
                print("Third transformation succeeded.")
            else:
                print("Third transformation failed.")
        else:
            print("Second transformation failed.")
    else:
        print("First transformation failed.")


    spark.stop()

if __name__ == "__main__":
    main()