from sqlalchemy import inspect, text

from database.connection import engine


def add_column_if_missing(table_name: str, column_name: str, column_definition: str):
    inspector = inspect(engine)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(table_name)
    }

    if column_name not in existing_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f"ALTER TABLE {table_name} "
                    f"ADD COLUMN {column_name} {column_definition}"
                )
            )
        print(f"Added column: {table_name}.{column_name}")
    else:
        print(f"Column already exists: {table_name}.{column_name}")


def main():
    print("Starting Assessment 4 database migration...")

    add_column_if_missing(
        "products",
        "category",
        "VARCHAR(100) NOT NULL DEFAULT 'General'"
    )

    add_column_if_missing(
        "products",
        "popularity",
        "INTEGER NOT NULL DEFAULT 0"
    )

    print("Assessment 4 database migration completed successfully.")


if __name__ == "__main__":
    main()