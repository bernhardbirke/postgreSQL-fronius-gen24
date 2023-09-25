#!/usr/bin/python

import psycopg2
from src.fronius_gen24.config import Configuration


class PostgresTasks:
    config = Configuration()

    def create_table_fronius_gen24(self) -> None:
        """create table fronius_gen24 in the PostgreSQL database (database specified in config.py), saves common inverter data"""
        command = """
        CREATE TABLE fronius_gen24 (
            data_id SERIAL PRIMARY KEY,
            time TIMESTAMP NOT NULL,
            PAC FLOAT4,
            IAC FLOAT4,
            UAC FLOAT4,
            FAC FLOAT4,
            TOTAL_ENERGY FLOAT4
        )
        """

        conn = None
        try:
            # read the connection parameters
            params = PostgresTasks.config.postgresql_config()
            # connect to the PostgreSQL server
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            # create table one by one
            cur.execute(command)
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def insert_fronius_gen24(
        self,
        PAC: int,
        IAC: float,
        UAC: float,
        FAC: float,
        TOTAL_ENERGY: float,
    ) -> int:
        """insert a new data row into the fronius_gen24 table"""
        sql = """INSERT INTO fronius_gen24(time, PAC, IAC, UAC, FAC, TOTAL_ENERGY)
                VALUES(NOW()::TIMESTAMP, %s, %s, %s, %s, %s) RETURNING data_id;"""
        conn = None
        data_id = None
        try:
            # read database configuration
            params = PostgresTasks.config.postgresql_config()
            # connect to the PostgreSQL database
            conn = psycopg2.connect(**params)
            # create a new cursor
            cur = conn.cursor()
            # execute the INSERT statement
            cur.execute(
                sql,
                (
                    PAC,
                    IAC,
                    UAC,
                    FAC,
                    TOTAL_ENERGY,
                ),
            )
            # get the generated id back
            data_id = cur.fetchone()[0]
            # commit the changes to the database
            conn.commit()
            # close communication with the database
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return data_id


# to test a specific function via "python postgresql_tasks.py" in the powershell
if __name__ == "__main__":
    postgres_task = PostgresTasks()
    postgres_task.create_table_fronius_gen24()
#   postgres_task.insert_fronius_gen24(84, 0.35999999999999999, 232.40000000000001, 49.969999999999999, 1734796.1200000001)
