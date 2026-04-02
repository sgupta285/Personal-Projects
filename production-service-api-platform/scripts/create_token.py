import argparse
from app.core.config import get_settings
from app.services.tokens import create_access_token


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", default="internal-admin")
    parser.add_argument("--token-type", choices=["oauth", "service"], default="oauth")
    parser.add_argument("--scope", action="append", default=["orders:read", "orders:write"])
    args = parser.parse_args()

    token = create_access_token(
        subject=args.client_id,
        scopes=args.scope,
        token_type=args.token_type,
        settings=get_settings(),
    )
    print(token)


if __name__ == "__main__":
    main()
