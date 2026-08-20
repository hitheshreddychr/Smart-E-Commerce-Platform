from sqlalchemy import inspect, text

from database.connection import engine


def add_column_if_missing(
    table_name: str,
    column_name: str,
    column_definition: str
):
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
                    f"ADD COLUMN {column_name} "
                    f"{column_definition}"
                )
            )

        print(
            f"Added column: "
            f"{table_name}.{column_name}"
        )

    else:

        print(
            f"Column already exists: "
            f"{table_name}.{column_name}"
        )


def create_payments_table():

    inspector = inspect(engine)

    if "payments" in inspector.get_table_names():

        print("Table already exists: payments")
        return

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                CREATE TABLE payments (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    order_id INTEGER NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    payment_method VARCHAR(50) NOT NULL DEFAULT 'stripe',
                    transaction_id VARCHAR(255),
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    INDEX ix_payments_id (id),
                    INDEX ix_payments_order_id (order_id),
                    INDEX ix_payments_transaction_id (transaction_id),
                    CONSTRAINT fk_payments_order
                        FOREIGN KEY (order_id)
                        REFERENCES orders(id)
                )
                """
            )
        )

    print("Created table: payments")


def main():

    print(
        "Starting Assessment 5 database migration..."
    )

    add_column_if_missing(
        "orders",
        "payment_status",
        "VARCHAR(50) NOT NULL DEFAULT 'pending'"
    )

    create_payments_table()

    print(
        "Assessment 5 database migration "
        "completed successfully."
    )


if __name__ == "__main__":
    main()