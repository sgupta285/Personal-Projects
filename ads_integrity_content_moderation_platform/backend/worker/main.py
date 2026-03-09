import logging

from app.db import Base, engine
from worker.consumer import run_consumer_forever

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def main() -> None:
    Base.metadata.create_all(bind=engine)
    run_consumer_forever()


if __name__ == "__main__":
    main()
